#!/usr/bin/env python

import os
import argparse
from ops import ArtifactHubOps


def main(args):
   dockerhub_url = None
   dockerhub_user = None
   dockerhub_password = None
   dockerhub_repository_owner = None
   dockerhub_auth_endpoint = None
   dockerhub_auth_scope = None
   dockerhub_auth_service = None

   if os.environ.get('DOCKERHUB_PASSWORD') != None: dockerhub_password = os.environ.get('DOCKERHUB_PASSWORD')
   if os.environ.get('DOCKERHUB_USER') != None: dockerhub_user = os.environ.get('DOCKERHUB_USER')
   if os.environ.get('DOCKERHUB_URL') != None: dockerhub_user = os.environ.get('DOCKERHUB_URL')
   if os.environ.get('OWNER_ID') != None: dockerhub_repository_owner = os.environ.get('OWNER_ID')
   if os.environ.get('DOCKERHUB_AUTH_ENDPOINT') != None: dockerhub_auth_endpoint = os.environ.get('DOCKERHUB_AUTH_ENDPOINT')
   if os.environ.get('DOCKERHUB_AUTH_SCOPE') != None: dockerhub_auth_scope = os.environ.get('DOCKERHUB_AUTH_SCOPE')
   if os.environ.get('DOCKERHUB_AUTH_SERVICE') != None: dockerhub_auth_service = os.environ.get('DOCKERHUB_AUTH_SERVICE')
   if args.password != None: dockerhub_password = args.password
   if args.user != None: dockerhub_user = args.user
   if args.hub != None: dockerhub_url = args.hub
   if args.owner != None: dockerhub_repository_owner = args.owner
   if args.endpoint != None: dockerhub_auth_endpoint = args.endpoint
   if args.scope != None: dockerhub_auth_scope = args.scope

   if dockerhub_user != None and dockerhub_password != None:
      dh_ops = ArtifactHubOps(dockerhub_user,dockerhub_password,dockerhub_url)
      if dockerhub_repository_owner != None:
         repo_names,repo_list = dh_ops.get_repo_list(dockerhub_repository_owner)
         for repo_name in repo_list:
            tag_names,tag_list = dh_ops.get_tag_list(repo_list[repo_name])
            if len(tag_names) > 0:
               for tag_name in tag_list:
                  for image in tag_list[tag_name]['images']:
                     print("{:>20}:{:<20} \t= {}".format(repo_name,tag_list[tag_name]['name'],image['digest']))

if __name__ == "__main__":
   parser = argparse.ArgumentParser()
   parser.add_argument("--user",help="dockerhub user")
   parser.add_argument("--password",help="dockerhub password")
   parser.add_argument("--owner",help="dockerhub repository list owner")
   parser.add_argument("--hub",help="url of hub")
   parser.add_argument("--endpoint",help="path to auth")
   parser.add_argument("--scope",help="authentication scope")

   args = parser.parse_args()
   main(args)
