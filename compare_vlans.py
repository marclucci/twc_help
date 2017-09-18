#!/usr/bin/env python
# Description: Check that vlans match on PROD and DR
# Author: Lucci
# Version: 1

import os, re, sys, glob
from optparse import OptionParser


switches = {
  "rd-core-1" : {},
  "fqdr-core-1" : {}
}


parser = OptionParser("%prog [options] $nodes\nCheck that vlans on switches match")

parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="Verbose mode")

(options, args) = parser.parse_args()



# Compare two lists for differences
def compare_lists(list1, list2):
  # Returns True if the lists match False otherwise

  diff_list = [item for item in list1 if not item in list2]

  diff_list2 = [item for item in list2 if not item in list1]

#  if (len(diff_list) > 0) or (len(diff_list2) > 0):
 #   return False

 # else:
#    return True



#
# Get latest configs
#

if options.verbose is True: sys.stdout.write("Finding the latest config files ...\n")

for switch in switches:
  highest_mtime = int()

  latest_config = ""

  switch_dict = switches[switch]

  for config_file in glob.iglob(switch + ".gw*"):
    if options.verbose: sys.stdout.write("Checking file " + config_file + " ...\n")

    mtime = os.stat(config_file).st_mtime

    if mtime > highest_mtime:
      latest_config = config_file

      highest_mtime = mtime

  # Build a dictionary of switch to latest config file
  switch_dict.update({"latest_config" : latest_config})



#
# Loop through configs looking for vlans
#

if options.verbose is True: sys.stdout.write("Reading the latest config files ...\n")

for switch in switches:
  switch_dict = switches[switch]

  switch_dict.update({
    "vlans" : {},
    "names" : {}
  })

  vlans_dict = switch_dict["vlans"]
  names_dict = switch_dict["names"]

  vlan = ""
  vlan_name = ""

  try:
    print ("Latest config: " + switch_dict["latest_config"])
    config_file_handle = open(switch_dict["latest_config"], "r")

  except IOError as err:
    sys.stderr.write("Failed to open latest config file for " + switch + "\n")

  for line in config_file_handle:
    line = line.rstrip()

    # Did we hit a new vlan?
    match = re.match("vlan ", line)

    if match is not None:
        if ',' not in line:
          if 'configuration' not in line:
            vlan = line.split()[-1]
            vlan_name = next(config_file_handle)
            vlan_name = vlan_name.split()[-1]


            if options.verbose is True: sys.stdout.write("Found a vlan " + vlan + "\n")

      # Add the vlan to the dictionary for this switch
          vlans_dict.update({
            vlan : vlan_name
          })
          names_dict.update({
            vlan + ':' + vlan_name : [vlan_name]
          })

  config_file_handle.close()



#
# Compare rd to dr

sys.stdout.write("\n\nVlans missing from DR\n\n\n") 

for vlan in sorted(switches["rd-core-1"]["vlans"]):

  try:
    if compare_lists(switches["rd-core-1"]["vlans"][vlan], switches["fqdr-core-1"]["vlans"][vlan]) is True:
        continue
 #      remove the continue above to check if the names do not match  
  #    sys.stdout.write("vlan " + vlan + " differs between fqdr-core-1 and rd-core-1!\n")

 
  except KeyError:
 #     name1 = str(vlans_dict[vlan])
  #    name1 = name1.strip("\n")
 #     name1 = name1.split(" ")
 #     name1 = name1[3]
      sys.stdout.write("vlan " + vlan + " " + vlan_name + " is missing on fqdr-core-1\n")



# Compare dr to rd

sys.stdout.write("\n\nVlans missing from PROD\n\n\n") 

for vlan in sorted(switches["fqdr-core-1"]["vlans"]):

  try:
     if compare_lists(switches["fqdr-core-1"]["vlans"][vlan], switches["rd-core-1"]["vlans"][vlan]) is True: 
        continue
#       remove the continue above to check if the names do not match      
#       sys.stdout.write("vlan " + vlan + str(vlans_dict[vlan]) + " differs between rd-core-1 and fqdr-core-1!\n")


  except KeyError:
      sys.stdout.write("vlan " + vlan + " " + vlan_name + " is missing on rd-core-1\n")
      

