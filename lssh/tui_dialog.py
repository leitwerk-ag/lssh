#! /usr/bin/env python3

import os, py_cui

def term_variable_workaround():
    term = os.environ.get("TERM")
    if term in ("xterm", "screen"):
        # These are values that py-cui cannot work with, so set it to xterm-256color
        os.putenv("TERM", "xterm-256color")

def flat_option_dialog(options, heading):
    '''
    Let the user choose an element from a list.

    Arguments:
      options:  A list of strings containing the options
      heading:  A header string to show above the dialog

    Return:     Returns the index of the chose element or None if the user
                aborted during selection.
    '''
    term_variable_workaround()
    root = py_cui.PyCUI(1, 1)
    result = [None] # array is used to make the value mutable for the return_entry function

    def return_entry():
        idx = menu.get_selected_item_index()
        result[0] = idx
        root.stop()

    menu = root.add_scroll_menu(heading, 0, 0)
    menu.add_item_list(options)
    menu.set_color(py_cui.WHITE_ON_BLACK)
    menu.set_selected_color(py_cui.BLACK_ON_WHITE)
    menu.add_key_command(py_cui.keys.KEY_ENTER, return_entry)

    root.move_focus(menu)

    root.start()
    return result[0]

def hierarchical_option_dialog(options, displaynames, heading_left, heading_right):
    '''
    Let the user choose an element from a two-layer hierarchical option tree.

    Arguments:
      options:       A list of tuples in the form (heading, child_elems) where
                     heading is a string naming one main node and child_elems
                     is a list of its subnodes.
      heading_left:  Header string for the main node option list
      heading_right: Header string for the subnodes option list

    Return:          Returns a tuple (idx1, idx2) where idx1 is the index of
                     the selected main node and idx2 is the index of the
                     selected subnode.
                     Or returns None if the user aborted during selection.
    '''
    term_variable_workaround()
    root = py_cui.PyCUI(1, 2)
    result = [None] # array is used to make the value mutable for inner functions
    left_idx = [0] # array for the same reason
    options_enumerated = list(enumerate(options))

    def heading_display(name):
        if name in displaynames:
            return displaynames[name]
        return name

    def option_sortkey(option):
        (enum_id, (heading, content)) = option
        display = heading_display(heading)
        return (display.lower(), display, heading)
    # Sort by display names (case-insensitive sort if possible)
    options_enumerated.sort(key=option_sortkey)

    def navigate_to_right():
        left_idx[0] = left_menu.get_selected_item_index()
        right_menu.clear()
        right_menu.add_item_list(options_enumerated[left_idx[0]][1][1])
        root.move_focus(right_menu)
        left_menu.set_selected_color(py_cui.WHITE_ON_BLUE)
        right_menu.set_selected_color(py_cui.BLACK_ON_WHITE)

    def navigate_to_left():
        root.move_focus(left_menu)
        left_menu.set_selected_color(py_cui.BLACK_ON_WHITE)
        right_menu.set_selected_color(py_cui.WHITE_ON_BLACK)

    def return_entry():
        right_idx = right_menu.get_selected_item_index()
        # return the two indices
        result[0] = (left_idx[0], right_idx)
        root.stop()

    def quit():
        root.stop()

    left_menu = root.add_scroll_menu(heading_left, 0, 0)
    left_menu.add_item_list([heading_display(entry[1][0]) for entry in options_enumerated])
    left_menu.set_color(py_cui.WHITE_ON_BLACK)
    left_menu.set_selected_color(py_cui.BLACK_ON_WHITE)
    left_menu.add_key_command(py_cui.keys.KEY_ENTER, navigate_to_right)
    left_menu.add_key_command(py_cui.keys.KEY_RIGHT_ARROW, navigate_to_right)
    left_menu.add_key_command(py_cui.keys.KEY_TAB, navigate_to_right)
    left_menu.add_key_command(py_cui.keys.KEY_Q_LOWER, quit)

    right_menu = root.add_scroll_menu(heading_right, 0, 1)
    right_menu.add_item_list(options[0][1])
    right_menu.set_color(py_cui.WHITE_ON_BLACK)
    right_menu.set_selected_color(py_cui.WHITE_ON_BLACK)
    right_menu.add_key_command(py_cui.keys.KEY_LEFT_ARROW, navigate_to_left)
    right_menu.add_key_command(py_cui.keys.KEY_BACKSPACE, navigate_to_left)
    right_menu.add_key_command(py_cui.keys.KEY_ENTER, return_entry)
    right_menu.add_key_command(py_cui.keys.KEY_Q_LOWER, quit)

    root.move_focus(left_menu)

    root.start()

    if result[0] is None:
        return None
    # Calculate the index back (entries were displayed in another order)
    left, right = result[0]
    left = options_enumerated[left][0]
    return (left, right)
