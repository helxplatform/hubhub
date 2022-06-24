from github import Github
from github.Organization import Organization

class GithubOps:
   def __init__(self,access_token):
      self._gh_handle = Github(login_or_token=access_token)

   def get_repos(self):
      repo_names = []
      for repo in self._gh_handle.get_user().get_repos():
         repo_names.append(repo.name)
      return repo_names

   def get_organization(self,org_id):
      return self._gh_handle.get_organization(org_id)
   
   def get_org_repo_list(self,org_obj):
      repo_list = {}
      repo_names = []
      for repo in org_obj.get_repos():
         repo_list[repo.name] = repo
         repo_names.append(repo.name)
      return repo_names,repo_list

   def get_tag_list(self,repo):
      tag_list = {}
      tag_names = []
      for tag in repo.get_tags():
         tag_list[tag.name] = tag
         tag_names.append(tag.name)
      return tag_names,tag_list
