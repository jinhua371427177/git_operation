#-*- coding: UTF-8 -*-
import urllib, urllib.request
import requests
import configparser
import json
import sys
import os
#import gitlab
from datetime import datetime
import re

def versionCompare(v1, v2):
    v1_check = re.match("\d+(\.\d+){0,2}", v1)
    v2_check = re.match("\d+(\.\d+){0,2}", v2)
    if v1_check is None or v2_check is None or v1_check.group() != v1 or v2_check.group() != v2:
        return 3
    v1_list = v1.split(".")
    v2_list = v2.split(".")
    v1_len = len(v1_list)
    v2_len = len(v2_list)
    if v1_len > v2_len:
        for i in range(v1_len - v2_len):
            v2_list.append("0")
    elif v2_len > v1_len:
        for i in range(v2_len - v1_len):
            v1_list.append("0")
    else:
        pass
    for i in range(len(v1_list)):
        if int(v1_list[i]) > int(v2_list[i]):
            return 1
        if int(v1_list[i]) < int(v2_list[i]):
            return 2
    return 0

def get_project_id(git_api_url, private_token, group_name, repo_name):
    project_id = 0
    group_id = 0
    try:
        get_groups_url = "%s/groups?private_token=%s" % (git_api_url, private_token)
        print(get_groups_url)
        response = requests.get(get_groups_url)
        groups = json.loads(response.text)
        #print(groups)
        for group in groups:
            if(group["full_name"] == group_name):
                group_id = group["id"]
                break
        print(group_id)
        get_projects_url = "%s/groups/%s/projects?private_token=%s" % (git_api_url, group_id, private_token)
        response = requests.get(get_projects_url)
        projects = json.loads(response.text)
        #print(projects)
        for project in projects:
            name = project["name"]
            #print(name)
            if name == repo_name:
                project_id = project["id"]
                break
    except Exception as e:
        print("get_project_id fail:%s/%s"%(group_name, repo_name))
        print (e)
    finally:
        return project_id

def get_last_tag_version(git_api_url, private_token, group_name, repo_name):
    lastTagVersion = ""
    versionList = []
    project_id = get_project_id(git_api_url, private_token, group_name, repo_name)
    if project_id == 0:
        return lastTagVersion
    print("Project ID:%s"%project_id)

    get_tags_url = "%s/projects/%s/repository/tags?private_token=%s"%(git_api_url, project_id, private_token)
    try:
        response = requests.get(get_tags_url)
        #print(response)
        tags = json.loads(response.text)
        #print(type(tags))
        #print(tags)
        for tag in tags:
            tagName = tag["name"]
            version = tagName.split("-")[-1]
            versionNum = len(version.split("."))
            if(versionNum != 3):
                continue
            versionList.append(version)
        print(versionList)
        for i in range(len(versionList)-1):
            for j in range(len(versionList)-i-1):
                if(versionCompare(versionList[j],versionList[j + 1]) == 1):
                    versionList[j], versionList[j + 1] = versionList[j + 1], versionList[j]
        lastTagVersion = versionList[-1]
    except Exception as e:
        print("get_latest_tag fail:" + get_tags_url)
        print (e)
        lastTagVersion = ""
    finally:
        print("lastTagVersion:%s"%lastTagVersion)
        return lastTagVersion

'''
git_api_url = "http://advgitlab.eastasia.cloudapp.azure.com/api/v3"
private_token = "HUJTr_z_-R8yYXsDzfNF"
group_name = "EI-PaaS SCADA"
repo_name = "wa-dashboard-server"
'''
git_api_url = sys.argv[1]
group_name = sys.argv[2]
repo_name = sys.argv[3]

tagVersion = get_last_tag_version(git_api_url, "yzLu8D6cD3ZRx_qsygt5", group_name, repo_name)

versionLog = open("lastversion.txt", 'w')
versionLog.write(tagVersion)
versionLog.close()


