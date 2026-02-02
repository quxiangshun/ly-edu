# -*- coding: utf-8 -*-
"""LyEdu API - Python 版本 (FastAPI)"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import config
from routers import auth, course, chapter, video, learning, user, department

app = FastAPI(title='LyEdu API', version='1.0.0')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

# 与前端 baseURL: '/api' 一致，所有接口挂到 /api 下
API_PREFIX = '/api'
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(course.router, prefix=API_PREFIX)
app.include_router(chapter.router, prefix=API_PREFIX)
app.include_router(video.router, prefix=API_PREFIX)
app.include_router(learning.router, prefix=API_PREFIX)
app.include_router(user.router, prefix=API_PREFIX)
app.include_router(department.router, prefix=API_PREFIX)


@app.get('/')
def root():
    return {'message': 'LyEdu API (Python)', 'docs': '/docs', 'api': API_PREFIX}


@app.get(API_PREFIX)
def api_root():
    return {'message': 'LyEdu API', 'docs': '/docs'}
