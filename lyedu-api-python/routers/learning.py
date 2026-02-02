# -*- coding: utf-8 -*-
"""学习路由"""
from typing import Optional
from fastapi import APIRouter, Header
from common.result import ResultCode, error_result, success
from models.schemas import JoinCourseRequest, VideoProgressRequest, PlayPingRequest
from services import user_course_service
from services import user_video_progress_service
from services import course_service
from services import video_service
from util.jwt_util import parse_authorization

router = APIRouter(prefix="/learning", tags=["learning"])

def _uid(auth: Optional[str]):
    return parse_authorization(auth)

@router.post("/join")
def join(body: JoinCourseRequest, authorization: Optional[str] = Header(None, alias="Authorization")):
    uid = _uid(authorization)
    if uid is None:
        return error_result(ResultCode.UNAUTHORIZED)
    user_course_service.join_course(uid, body.course_id)
    return success()

@router.get("/my-courses")
def my_courses(authorization: Optional[str] = Header(None, alias="Authorization")):
    uid = _uid(authorization)
    if uid is None:
        return error_result(ResultCode.UNAUTHORIZED)
    return success(user_course_service.list_by_user_id(uid))

@router.post("/video-progress")
def video_progress(body: VideoProgressRequest, authorization: Optional[str] = Header(None, alias="Authorization")):
    uid = _uid(authorization)
    if uid is None:
        return error_result(ResultCode.UNAUTHORIZED)
    user_video_progress_service.update_progress(uid, body.video_id, progress=body.progress or 0, duration=body.duration or 0)
    video = video_service.get_by_id(body.video_id)
    if video and video.get("course_id"):
        user_course_service.join_course(uid, video["course_id"])
        course_videos = video_service.list_by_course_id(video["course_id"])
        video_ids = [v["id"] for v in course_videos]
        progress_map = user_video_progress_service.get_progress_map(uid, video_ids)
        total_duration = sum(v.get("duration") or 0 for v in course_videos if (v.get("duration") or 0) > 0)
        finished_duration = 0
        for v in course_videos:
            d = v.get("duration") or 0
            if d <= 0:
                continue
            p = progress_map.get(v["id"])
            if p and p.get("progress") is not None:
                finished_duration += min(p["progress"], d)
        percent = int(finished_duration * 100 / total_duration) if total_duration > 0 else 0
        user_course_service.update_progress(uid, video["course_id"], min(100, percent))
    return success()

@router.post("/play-ping")
def play_ping(body: PlayPingRequest, authorization: Optional[str] = Header(None, alias="Authorization")):
    uid = _uid(authorization)
    if uid is None:
        return error_result(ResultCode.UNAUTHORIZED)
    user_video_progress_service.update_last_play_ping(uid, body.video_id)
    return success()

@router.get("/video-progress/{videoId}")
def get_video_progress(videoId: int, authorization: Optional[str] = Header(None, alias="Authorization")):
    uid = _uid(authorization)
    if uid is None:
        return error_result(ResultCode.UNAUTHORIZED)
    progress = user_video_progress_service.get_by_user_and_video(uid, videoId)
    return success(progress)

@router.get("/watched-courses")
def watched_courses(authorization: Optional[str] = Header(None, alias="Authorization")):
    uid = _uid(authorization)
    if uid is None:
        return error_result(ResultCode.UNAUTHORIZED)
    try:
        course_ids = user_video_progress_service.list_watched_course_ids(uid)
        if not course_ids:
            return success([])
        seen = list(dict.fromkeys(course_ids))
        result = []
        for cid in seen:
            if not cid or cid <= 0:
                continue
            try:
                c = course_service.get_detail_by_id(cid)
                if not c:
                    continue
                videos = video_service.list_by_course_id(cid)
                progress_percent = 0
                if videos:
                    video_ids = [v["id"] for v in videos]
                    progress_map = user_video_progress_service.get_progress_map(uid, video_ids)
                    total_duration = 0
                    finished_duration = 0
                    for v in videos:
                        d = v.get("duration") or 0
                        if d <= 0:
                            continue
                        total_duration += d
                        p = progress_map.get(v["id"])
                        if p and p.get("progress") is not None:
                            finished_duration += min(p["progress"], d)
                    progress_percent = int(finished_duration * 100 / total_duration) if total_duration > 0 else 0
                    progress_percent = min(100, progress_percent)
                uc = user_course_service.get_by_user_and_course(uid, cid)
                if uc and (uc.get("progress") or 0) > progress_percent:
                    progress_percent = uc["progress"]
                result.append({"course": c, "progress": progress_percent})
            except Exception:
                pass
        return success(result)
    except Exception:
        return success([])
