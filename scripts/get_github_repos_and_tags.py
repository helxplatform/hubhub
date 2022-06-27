#!/usr/bin/env python

import os
import argparse
from ops import GithubOps


def main(args):
   access_token = None
   org_id = None

   if os.environ.get('ACCESS_TOKEN') != None: access_token = os.environ.get('ACCESS_TOKEN')
   if os.environ.get('ORG_ID') != None: ord_id = os.environ.get('ORD_ID')
   if args.access_token != None: access_token = args.access_token
   if args.org != None: org_id = args.org

   if access_token != None:
      gh_ops = GithubOps(access_token)
      if org_id != None:
         org = gh_ops.get_organization(org_id)
         repo_names,repo_list = gh_ops.get_org_repo_list(org)
         for repo_name in repo_list:
            tag_names,tag_list = gh_ops.get_tag_list(repo_list[repo_name])
            if len(tag_names) > 0:
               for tag_name in tag_list:
                  print("{:>30}:{:<20} \t= {}".format(repo_name,tag_list[tag_name].name,tag_list[tag_name].commit.sha))
      else:
         repo_names,repo_list = gh_ops.get_repo_list()
         print(repo_names)

if __name__ == "__main__":
   parser = argparse.ArgumentParser()
   parser.add_argument("--access_token",help="github access token")
   parser.add_argument("--org",help="github organization")

   args = parser.parse_args()
   main(args)