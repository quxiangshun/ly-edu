# -*- coding: utf-8 -*-
"""证书模板路由，与 Java CertificateTemplateController 对应"""
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from common.result import error_result, success
from services import certificate_template_service

router = APIRouter(prefix="/certificate-template", tags=["certificate-template"])


class CertificateTemplateRequest(BaseModel):
    name: str = ""
    description: Optional[str] = None
    config: Optional[str] = None
    sort: Optional[int] = 0
    status: Optional[int] = 1


@router.get("/list")
def list_all():
    return success(certificate_template_service.list_all())


@router.get("/{template_id}")
def get_by_id(template_id: int):
    t = certificate_template_service.get_by_id(template_id)
    if not t:
        return error_result((404, "资源不存在"))
    return success(t)


@router.post("")
def create(body: CertificateTemplateRequest):
    entity = {
        "name": body.name,
        "description": body.description,
        "config": body.config,
        "sort": body.sort or 0,
        "status": body.status or 1,
    }
    rid = certificate_template_service.save(entity)
    return success(rid)


@router.put("/{template_id}")
def update(template_id: int, body: CertificateTemplateRequest):
    t = certificate_template_service.get_by_id(template_id)
    if not t:
        return error_result((404, "资源不存在"))
    entity = {
        "id": template_id,
        "name": body.name,
        "description": body.description,
        "config": body.config,
        "sort": body.sort or 0,
        "status": body.status or 1,
    }
    certificate_template_service.update(entity)
    return success(None)


@router.delete("/{template_id}")
def delete(template_id: int):
    t = certificate_template_service.get_by_id(template_id)
    if not t:
        return error_result((404, "资源不存在"))
    certificate_template_service.delete(template_id)
    return success(None)
