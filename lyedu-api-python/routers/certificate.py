# -*- coding: utf-8 -*-
"""证书颁发规则路由，与 Java CertificateController 对应"""
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from common.result import error_result, success
from services import certificate_service

router = APIRouter(prefix="/certificate", tags=["certificate"])


class CertificateRequest(BaseModel):
    templateId: Optional[int] = None
    name: str = ""
    sourceType: str = ""
    sourceId: Optional[int] = None
    sort: Optional[int] = 0
    status: Optional[int] = 1


@router.get("/list")
def list_all():
    return success(certificate_service.list_all())


@router.get("/{cert_id}")
def get_by_id(cert_id: int):
    c = certificate_service.get_by_id(cert_id)
    if not c:
        return error_result((404, "资源不存在"))
    return success(c)


@router.post("")
def create(body: CertificateRequest):
    if body.templateId is None or body.sourceId is None:
        return error_result((400, "模板ID和来源ID不能为空"))
    entity = {
        "templateId": body.templateId,
        "name": body.name,
        "sourceType": body.sourceType,
        "sourceId": body.sourceId,
        "sort": body.sort or 0,
        "status": body.status or 1,
    }
    rid = certificate_service.save(entity)
    return success(rid)


@router.put("/{cert_id}")
def update(cert_id: int, body: CertificateRequest):
    c = certificate_service.get_by_id(cert_id)
    if not c:
        return error_result((404, "资源不存在"))
    entity = {
        "id": cert_id,
        "templateId": body.templateId,
        "name": body.name,
        "sourceType": body.sourceType,
        "sourceId": body.sourceId,
        "sort": body.sort or 0,
        "status": body.status or 1,
    }
    certificate_service.update(entity)
    return success(None)


@router.delete("/{cert_id}")
def delete(cert_id: int):
    c = certificate_service.get_by_id(cert_id)
    if not c:
        return error_result((404, "资源不存在"))
    certificate_service.delete(cert_id)
    return success(None)
