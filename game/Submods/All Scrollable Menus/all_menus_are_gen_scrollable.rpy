init -990 python in mas_submod_utils:
    Submod(
        author="multimokia",
        name="All Gen Scrollable Menus",
        description="A submod which converts all menus to gen-scrollable-menus so Monika's face is never hidden.",
        version="1.0.0",
        version_updates={}
    )

init 900 python:
    def menu_override(items, set_expr):
        """
        For the docstring DM Tom: 152088707963289600

        :pcrowSip:
        """
        global _history_list
        global _window_auto

        if renpy.config.old_substitutions:
            def substitute(s):
                return s % renpy.exports.tag_quoting_dict
        else:
            def substitute(s):
                return s

        #Filter the list of items to only include ones for which the condition is True.
        items = [
            (substitute(label), value)
            for label, condition, value in items
            if renpy.python.py_eval(condition)
        ]

        #Check to see if there's at least one choice in set of items:
        if not items:
            return None

        #Filter the list of items on the set_expr:
        if set_expr:
            set = renpy.python.py_eval(set_expr)
            items = [
                (label, value)
                for label, value in items
                if label not in set
            ]

        else:
            set = None

        #Convert items
        formatted_menuitems = [
            (x[0], x[1], False, False)
            for x in items
        ]

        #Prep before showing the menu
        renpy.show("monika", at_list=[t21])

        #Get last line
        last_line = _history_list[-1].what

        if last_line.endswith("{nw}"):
            renpy.say(m, last_line.replace("{nw}", "{fast}"), interact=False)
            _history_list.pop()

        else:
            _window_hide()

        picked = renpy.call_screen(
            "mas_gen_scrollable_menu",
            items=formatted_menuitems,
            display_area=store.mas_ui.SCROLLABLE_MENU_TXT_AREA,
            scroll_align=store.mas_ui.SCROLLABLE_MENU_XALIGN
        )

        #Reset Monika's position
        renpy.show("monika", at_list=[t11])

        #And reset the window
        _window_auto = True

        #If we have a set, fill it in with the label of the chosen item.
        if set is not None and picked is not None:
            for label, value in items:
                if value == picked:
                    try:
                        set.append(label)
                    except AttributeError:
                        set.add(label)

        return picked

    renpy.exports.menu = menu_override
