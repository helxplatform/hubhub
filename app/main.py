import threading
import os
import yaml
import logging
from fastapi import FastAPI
from fastapi.logger import logger
from pydantic import BaseModel,BaseSettings
from typing import List,Dict,Any,AnyStr,Union
from time import sleep
from ops import GithubOps,ArtifactHubOps


class Settings(BaseSettings):
   containers_organization: str = None
   containers_password: str = None
   containers_url: str = None
   containers_user: str = None
   dockerhub_organization: str = None
   dockerhub_password: str = None
   dockerhub_url: str = None
   dockerhub_user: str = None
   github_access_token: str = None
   github_organization: str = None

class Artifact(BaseModel):
   repository_name: str = ""
   digest: str = ""

class Tag(BaseModel):
   tag_name: str = ""
   github_repository_name: str = ""
   github_commit_hash: str = ""
   artifacts: Dict[str,Artifact] = {}

class Project(BaseModel):
   repository_name: str = ""
   tags: Dict[str,Tag] = {}

class ProjectList(BaseModel):
   projects: Dict[str,Project] = {}

class Resolver(threading.Thread):
   def __init__(self,log,github_ops,dockerhub_ops,containers_ops,group=None,target=None,name=None,args=(),kwargs=None):
      threading.Thread.__init__(self,group=group,target=target,name=name,args=args,kwargs=kwargs)
      self._log = log
      self._settings = settings
      self._current = ProjectList()
      self._github_ops = github_ops
      self._dockerhub_ops = dockerhub_ops
      self._containers_ops = containers_ops

   def new_github_info(self):
      info = ProjectList()
      if self._github_ops != None and self._settings.github_organization != None:
         org = self._github_ops.get_organization(self._settings.github_organization)
         repo_names,repo_list = self._github_ops.get_org_repo_list(org)
         for repo_name in repo_list:
            info.projects[repo_name] = Project()
            info.projects[repo_name].repository_name = repo_name
            tag_names,tag_list = self._github_ops.get_tag_list(repo_list[repo_name])
            for tag_name in tag_list:
               new_tag = Tag()
               new_tag.tag_name = tag_name
               new_tag.github_commit_hash = tag_list[tag_name].commit.sha
               new_tag.github_repository_name = repo_name
               info.projects[repo_name].tags[tag_name] = new_tag
      return info
   
   def merge_dockerhub_info(self,info):
      if self._settings.dockerhub_organization != None:
         repo_names,repo_list = self._dockerhub_ops.get_repo_list(self._settings.dockerhub_organization)
         for repo_name in repo_list:
            if info.projects.get(repo_name,None) == None:
               info.projects[repo_name] = Project()
               info.projects[repo_name].repository_name = repo_name
            tag_names,tag_list = self._dockerhub_ops.get_tag_list(repo_list[repo_name])
            for tag_name in tag_list:
               if len(tag_list[tag_name]['images']) >= 1:
                  if info.projects[repo_name].tags.get(tag_name,None) == None:
                     new_tag = Tag()
                     new_tag.tag_name = tag_name
                     info.projects[repo_name].tags[tag_name] = new_tag
                  new_artifact = Artifact()
                  new_artifact.repository_name = repo_name
                  new_artifact.digest = tag_list[tag_name]['images'][0]['digest']
                  info.projects[repo_name].tags[tag_name].artifacts["dockerhub"] = new_artifact

   def merge_containers_info(self,info):
      if self._settings.containers_organization != None:
         repo_names,repo_list = self._containers_ops.get_repo_list(self._settings.containers_organization)
         for repo_name in repo_list:
            if info.projects.get(repo_name,None) == None:
               info.projects[repo_name] = Project()
               info.projects[repo_name].repository_name = repo_name
            tag_names,tag_list = self._containers_ops.get_tag_list(repo_list[repo_name])
            for tag_name in tag_list:
               if info.projects[repo_name].tags.get(tag_name,None) == None:
                  new_tag = Tag()
                  new_tag.tag_name = tag_name
                  info.projects[repo_name].tags[tag_name] = new_tag
               new_artifact = Artifact()
               new_artifact.repository_name = repo_name
               new_artifact.digest = tag_list[tag_name]['digest']
               info.projects[repo_name].tags[tag_name].artifacts["containers"] = new_artifact

   def run(self):
      done = False
      self._log.info("running...")
      while not done:
         self._log.info("getting info from github")
         info = self.new_github_info()
         self._log.info("getting info from dockerhub")
         self.merge_dockerhub_info(info)
         self._log.info("getting info from containers")
         self.merge_containers_info(info)
         self._current = info
         sleep(300)

   def get_current(self):
      return self._current

app = FastAPI()
settings = Settings()

def init_settings():
   values = {}
   if os.environ.get('VALUES_FILE') != None: 
      with open(os.environ.get('VALUES_FILE'),'r') as stream: values = yaml.safe_load(stream)
      settings.containers_password = values.get('containers_password')
      settings.containers_user = values.get('containers_user')
      settings.containers_url = values.get('containers_url')
      settings.containers_organization = values.get('containers_org')
      settings.dockerhub_password = values.get('dockerhub_password')
      settings.dockerhub_user = values.get('dockerhub_user')
      settings.dockerhub_url = values.get('dockerhub_url')
      settings.dockerhub_organization = values.get('dockerhub_org')
      settings.github_access_token = values.get('github_access_token')
      settings.github_organization = values.get('github_org')

   if os.environ.get('CONTAINERS_PASSWORD') != None: settings.containers_password = os.environ.get('CONTAINERS_PASSWORD')
   if os.environ.get('CONTAINERS_USER') != None: settings.containers_user = os.environ.get('CONTAINERS_USER')
   if os.environ.get('CONTAINERS_URL') != None: settings.containers_url = os.environ.get('CONTAINERS_URL')
   if os.environ.get('CONTAINERS_ORG') != None: settings.containers_organization = os.environ.get('CONTAINERS_ORG')
   if os.environ.get('DOCKERHUB_PASSWORD') != None: settings.dockerhub_password = os.environ.get('DOCKERHUB_PASSWORD')
   if os.environ.get('DOCKERHUB_USER') != None: settings.dockerhub_user = os.environ.get('DOCKERHUB_USER')
   if os.environ.get('DOCKERHUB_URL') != None: settings.dockerhub_url = os.environ.get('DOCKERHUB_URL')
   if os.environ.get('DOCKERHUB_ORG') != None: settings.dockerhub_organization = os.environ.get('DOCKERHUB_ORG')
   if os.environ.get('GITHUB_ACCESS_TOKEN') != None: settings.github_access_token = os.environ.get('GITHUB_ACCESS_TOKEN')
   if os.environ.get('GITHUB_ORG') != None: settings.github_organization = os.environ.get('GITHUB_ORG')

@app.on_event("startup")
async def startup_event():
   global resolver

   resolver = None
   log = logging.getLogger("uvicorn")
   github_ops = None
   dockerhub_ops = None
   containers_ops = None
   init_settings()
   if settings.github_access_token != None: github_ops = GithubOps(settings.github_access_token)
   if settings.dockerhub_user != None and settings.dockerhub_password != None:
      dockerhub_ops = ArtifactHubOps(
         settings.dockerhub_user,
         settings.dockerhub_password,
         settings.dockerhub_url
      )
   if settings.containers_user != None and settings.containers_password != None:
      containers_ops = ArtifactHubOps(
         settings.containers_user,
         settings.containers_password,
         settings.containers_url,
         prefix="api/v2.0",
         hub_type="opencontainer",
         auth_endpoint="service/token",
         args={ "service":"harbor-registry", "scope":"repository" }
      )
   if github_ops != None and dockerhub_ops != None and containers_ops != None:
      resolver = Resolver(log,github_ops,dockerhub_ops,containers_ops)
      resolver.start()

@app.get("/app/current",response_model=ProjectList)
async def get_current():
   if resolver != None: return resolver.get_current()
   else: return {}