#!/usr/bin/env  python3
# -*- coding: utf-8 -*-
"""
 File Name：  cisco01
 Author :  seven
 Change Activity:
     2018/11/11:
"""

from ciscoconfparse import CiscoConfParse

def standardize_intfs(parse):

    ## Search all switch interfaces and modify them
    #
    # r'^interface.+?thernet' is a regular expression, for ethernet intfs
    for intf in parse.find_objects(r'^interface.+?thernet'):

        has_stormcontrol = intf.has_child_with(r' storm-control broadcast')
        is_switchport_access = intf.has_child_with(r'switchport mode access')
        is_switchport_trunk = intf.has_child_with(r'switchport mode trunk')

        ## Add missing features
        if is_switchport_access and (not has_stormcontrol):
            intf.append_to_family(' storm-control action trap')
            intf.append_to_family(' storm-control broadcast level 0.4 0.3')

        ## Remove dot1q trunk misconfiguration...
        elif is_switchport_trunk:
            intf.delete_children_matching('port-security')

## Parse the config
parse = CiscoConfParse('short.conf')

## Add a new switchport at the bottom of the config...
parse.append_line('interface FastEthernet0/4')
parse.append_line(' switchport')
parse.append_line(' switchport mode access')
parse.append_line('!')
parse.commit()     # commit() **must** be called before searching again

## Search and standardize the interfaces...
standardize_intfs(parse)
parse.commit()     # commit() **must** be called before searching again

## I'm illustrating regular expression usage in has_line_with()
if not parse.has_line_with(r'^service\stimestamp'):
    ## prepend_line() adds a line at the top of the configuration
    parse.prepend_line('service timestamps debug datetime msec localtime show-timezone')
    parse.prepend_line('service timestamps log datetime msec localtime show-timezone')

## Write the new configuration
parse.save_as('short.conf.new')