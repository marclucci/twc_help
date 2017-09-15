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

  if (len(diff_list) > 0) or (len(diff_list2) > 0):
    return False

  else:
    return True



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
    "vlans" : {}
  })

  vlans_dict = switch_dict["vlans"]

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
          vlan = line.split()[-1]
          vlan_name = next(config_file_handle)

          if options.verbose is True: sys.stdout.write("Found a vlan " + vlan + "\n")

      # Add the vlan to the dictionary for this switch
          vlans_dict.update({
            vlan + ":" + vlan_name : []
          })

          continue

    # find next vlan
    match = re.match(" name", line)

    if match is not None:
      if options.verbose is True: sys.stdout.write("Found a new vlan " + vlan + " : " + line + "\n")

      current_vlan_list = vlans_dict[vlan]

      current_vlan_list.append(line)

  config_file_handle.close()



#
# Compare the lists 

#if options.verbose is True: sys.stdout.write("Comparing vlans for rd-core-1 vs fqdr-core-1 ...\n")
#sys.stdout.write("\n")
#
#for vlan in sorted(switches["rd-core-1"]["vlans"]):
#  if options.verbose is True: sys.stdout.write("Checking vlans: " + vlan + "\n")
#
#                      
#  try:
#    if compare_lists(switches["rd-core-1"]["vlans"][vlan], switches["fqdr-core-1"]["vlans"][vlan]) is False:
#      sys.stdout.write("vlan " + vlan + " differs between fqdr-core-1 and rd-core-1!\n")

#      for rule in switches["rd-core-1"]["vlans"][vlan]:
#        if rule not in switches["fqdr-core-1"]["vlans"][vlan]:
#          sys.stdout.write("     Missing vlan on fqdr-core-1: " + rule + "\n")

#      for rule in switches["fqdr-core-1"]["vlans"][vlan]:
#        if rule not in switches["rd-core-1"]["vlans"][vlan]:
#          sys.stdout.write("     Missing vlan on rd-core-1: " + rule + "\n")

  except KeyError:
    sys.stdout.write("vlan " + vlan + " is missing on fqdr-core-1 (exists on rd-core-1)!\n")



# Compare the lists 

if options.verbose is True: sys.stdout.write("Comparing vlans for dr and prod ...\n")
sys.stdout.write("\n")
#
for vlan in sorted(switches["fqdr-core-1"]["vlans"]):
  if options.verbose is True: sys.stdout.write("Checking vlans: " + vlan + "\n")

  try:
    if compare_lists(switches["fqdr-core-1"]["vlans"][vlan], switches["rd-core-1"]["vlans"][vlan]) is False:
      sys.stdout.write("vlan " + vlan + " differs between rd-core-1 and fqdr-core-1!\n")

#      for rule in switches["fqdr-core-1"]["vlans"][vlan]:
#        if rule not in switches["rd-core-1"]["vlans"][vlan]:
#          sys.stdout.write("     Missing vlan on rd-core-1: " + rule + "\n")
#
#      for rule in switches["rd-core-1"]["vlans"][vlan]:
#        if rule not in switches["fqdr-core-1"]["vlans"][vlan]:
#          sys.stdout.write("     Missing rule on rd-core-1: " + rule + "\n")

  except KeyError:
    sys.stdout.write("vlan " + vlan + vlan_name + " is missing on rd-core-1 (exists on fqdr-core-1)!\n")
