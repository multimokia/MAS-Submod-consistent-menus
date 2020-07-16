default persistent._gsm_use_talk_choice = False

init -990 python in mas_submod_utils:
    Submod(
        author="multimokia",
        name="All Gen Scrollable Menus",
        description="A submod which converts all menus to gen-scrollable-menus so Monika's face is never hidden.",
        version="1.0.1",
        version_updates=dict(),
        settings_pane="gsm_settings"
    )

#START: Settings Pane
screen gsm_settings():
    vbox:
        box_wrap False
        xfill True
        xmaximum 1000

        hbox:
            style_prefix "check"
            box_wrap False

            textbutton "Use Talk Choice Screen":
                action ToggleField(persistent, "_gsm_use_talk_choice")
                selected persistent._gsm_use_talk_choice


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

        #Prep before showing the menu
        renpy.show("monika", at_list=[t21])

        #Get last line
        last_line = _history_list[-1].what

        #Handle the textbox show to keep the question up during the menu
        if last_line.endswith("{nw}"):
            renpy.say(m, last_line.replace("{nw}", "{fast}"), interact=False)

        elif last_line.endswith("{fast}"):
            renpy.say(m, last_line, interact=False)

        #Otherwise no text, and we should hide the textbox instead
        else:
            _window_hide()

        #If the user wishes to use the talk-choice menu, we'll need to parse the input accordingly
        if persistent._gsm_use_talk_choice:
            menu_items = list()

            #Get the location of the menu as MenuEntries need it
            location=renpy.game.context().current

            #And now make a formatted list of menu_items
            for (label, value) in items:
                if value is not None:
                    action = renpy.ui.ChoiceReturn(label, value, location)
                    chosen = action.get_chosen()

                else:
                    action = None
                    chosen = False

                if renpy.config.choice_screen_chosen:
                    me = renpy.MenuEntry((label, action, chosen))
                else:
                    me = renpy.MenuEntry((label, action))

                me.caption = label
                me.action = action
                me.chosen = chosen
                menu_items.append(me)

            #Then call the screen for it
            picked = renpy.call_screen(
                "talk_choice",
                items=menu_items
            )

        #Otherwise, we use the gen scrollable menu
        else:
            #Convert items to the 4 part tuple
            formatted_menuitems = [
                (x[0], x[1], False, False)
                for x in items
            ]

            #And show the screen
            picked = renpy.call_screen(
                "mas_gen_scrollable_menu",
                items=formatted_menuitems,
                display_area=store.mas_ui.SCROLLABLE_MENU_TXT_AREA,
                scroll_align=store.mas_ui.SCROLLABLE_MENU_XALIGN
            )

        #Reset Monika's position
        renpy.show("monika", at_list=[t11])

        #Reset the window
        _window_auto = True

        #And pop from hist
        if last_line.endswith("{fast}"):
            _history_list.pop()

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
