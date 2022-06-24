from dockerhub_api import DockerHub

class ArtifactHubOps:
   def __init__(self,username,password,url,hub_type="dockerhub",prefix="v2",auth_endpoint=None,args={}):
      self._hub_type = hub_type
      if hub_type == "dockerhub":
         self._hub_handle = DockerHub(method=1,username=username,password=password,url=url,version=prefix,args=args)
      else:
         self._hub_handle = DockerHub(method=2,username=username,password=password,url=url,version=prefix,auth_endpoint=auth_endpoint,args=args)
   
   def get_repo_list(self,owner):
      repo_list = {}
      repo_names = []
      repos = []
      if self._hub_type == "dockerhub": repos = self._hub_handle.repositories(owner)
      else: repos = self._hub_handle.project_repositories(owner)
      for repo in repos:
         repo_name = repo.get('name')
         repo_list[repo_name] = repo
         repo_names.append(repo_name)
      return repo_names,repo_list

   def get_tag_list(self,repo):
      tag_list = {}
      tag_names = []
      if self._hub_type == "dockerhub":
         tags = self._hub_handle.tags(repo['namespace'],repo['name'])
         for tag in tags:
            tag_name = tag.get('name')
            tag_list[tag_name] = tag
            tag_names.append(tag_name)
      else: 
         project_name = repo['name'].split('/')[0]
         repo_name = repo['name'].split('/')[1]
         artifacts = self._hub_handle.project_artifacts(project_name,repo_name,params={ "with_tag":True, "with_label":False, "with_scan_overview":False, "with_signature":False, "with_immutable_status":False, "with_accessory":False })
         for artifact in artifacts:
            if artifact.get('tags',None) != None:
               for tag in artifact['tags']: 
                  tag_name = tag.get('name')
                  tag_list[tag_name] = tag
                  tag_list[tag_name]['digest'] = artifact['digest']
                  tag_names.append(tag_name)
      return tag_names,tag_list

