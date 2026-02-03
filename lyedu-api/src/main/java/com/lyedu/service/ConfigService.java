package com.lyedu.service;

import com.lyedu.entity.Config;

import java.util.List;

public interface ConfigService {

    String getByKey(String configKey);

    List<Config> listByCategory(String category);

    List<Config> listAll();

    void set(String configKey, String configValue, String category, String remark);
}
