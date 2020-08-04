default persistent._gsm_menu_style = gsm_utils.TYPE_SCROLLABLE

init -990 python in mas_submod_utils:
    Submod(
        author="multimokia",
        name="All Gen Scrollable Menus",
        description="A submod which converts all menus to gen-scrollable-menus so Monika's face is never hidden.",
        version="1.0.3",
        settings_pane="gsm_settings",
        version_updates={
            "multimokia_all_gen_scrollable_menus_v1_0_0": "multimokia_all_gen_scrollable_menus_v1_0_2",
            "multimokia_all_gen_scrollable_menus_v1_0_1": "multimokia_all_gen_scrollable_menus_v1_0_2"
        }
    )

#START: Update scripts
label multimokia_all_gen_scrollable_menus_v1_0_0(version="v1_0_0"):
    return

label multimokia_all_gen_scrollable_menus_v1_0_1(version="v1_0_1"):
    return

label multimokia_all_gen_scrollable_menus_v1_0_2(version="v1_0_2"):
    python:
        safeDel("_gsm_use_talk_choice")
        safeDel("_gsm_unobstructed_choice")
    return


#START: Settings Pane
screen gsm_settings():
    vbox:
        box_wrap False
        xfill True
        xmaximum 1000

        hbox:
            style_prefix "check"
            box_wrap False

            textbutton "Use Gen Scrollable Menu":
                action SetField(persistent, "_gsm_menu_style", gsm_utils.TYPE_SCROLLABLE)
                selected persistent._gsm_menu_style == gsm_utils.TYPE_SCROLLABLE

            textbutton "Use Talk Choice Screen":
                action SetField(persistent, "_gsm_menu_style", gsm_utils.TYPE_CHOICE_MENU)
                selected persistent._gsm_menu_style == gsm_utils.TYPE_CHOICE_MENU

            textbutton "Use Unobstructed Choice Screen":
                action SetField(persistent, "_gsm_menu_style", gsm_utils.TYPE_UNOBSTRUCTED_CHOICE_MENU)
                selected persistent._gsm_menu_style == gsm_utils.TYPE_UNOBSTRUCTED_CHOICE_MENU

init -1 python in gsm_utils:
    import store

    TYPE_SCROLLABLE = "mas_gen_scrollable_menu"
    TYPE_CHOICE_MENU = "talk_choice"
    TYPE_UNOBSTRUCTED_CHOICE_MENU = "unobstructed_choice"

    def parse_to_gen_scrollable(items):
        """
        Converts the list of items to a 4 part tuple used for the mas_gen_scrollable_menu

        IN:
            items - a tuple of (label, value) representing menuitems

        OUT:
            tuple - (label, value, False, False) representing menuitems in mas_gen_scrollable_menu format
        """
        #Convert items to the 4 part tuple
        return [
            (x[0], x[1], False, False)
            for x in items
        ]

    def parse_to_standard_renpy_menu(items):
        """
        Converts the list of items to the standard list of MenuEntry objects renpy uses for menus

        IN:
            items - a tuple of (label, value) representing menuitems

        OUT:
            list of MenuEntry objects representing menuitems in standard renpy format
        """
        menu_items = list()

        #Get the location of the menu as MenuEntries need it
        location = renpy.game.context().current

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

        return menu_items

    #Now build maps for these
    TYPE_PARSE_MAP = {
        TYPE_SCROLLABLE: parse_to_gen_scrollable,
        TYPE_CHOICE_MENU: parse_to_standard_renpy_menu,
        TYPE_UNOBSTRUCTED_CHOICE_MENU: parse_to_standard_renpy_menu,
    }

    TYPE_KWARGS_MAP = {
        TYPE_SCROLLABLE: {
            "display_area": store.mas_ui.SCROLLABLE_MENU_TXT_TALL_AREA,
            "scroll_align": store.mas_ui.SCROLLABLE_MENU_XALIGN
        }
    }

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
        if (
            renpy.showing("monika")
            and persistent._gsm_menu_style != gsm_utils.TYPE_UNOBSTRUCTED_CHOICE_MENU
        ):
            renpy.show("monika", at_list=[t21])


        #Get last line if it exists
        last_line = _history_list[-1].what if _history_list else ""

        #Local var for use later
        window_hidden = False

        #Handle the textbox show to keep the question up during the menu
        if last_line.endswith("{nw}"):
            renpy.say(m, last_line.replace("{nw}", "{fast}"), interact=False)

        elif last_line.endswith("{fast}"):
            renpy.say(m, last_line, interact=False)

        #Otherwise no text, and we should hide the textbox instead
        else:
            _window_hide()
            #Since we set window to hide, we'll need to reset the window to auto after
            window_hidden = True

        #Parse menu items
        formatted_items = gsm_utils.TYPE_PARSE_MAP[persistent._gsm_menu_style](items)

        #If the screen takes kwargs, we'll handle that here
        picked = renpy.call_screen(
            persistent._gsm_menu_style,
            items=formatted_items,
            **gsm_utils.TYPE_KWARGS_MAP.get(persistent._gsm_menu_style, dict())
        )

        #Reset Monika's position
        if renpy.showing("monika"):
            renpy.show("monika", at_list=[t11])

        #Set window to auto again if we hid it
        if window_hidden:
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

#Unobstructed menu screen and styles
screen unobstructed_choice(items):
    style_prefix "unobstructedchoice"

    vbox:
        for i in items:
            textbutton i.caption action i.action


style unobstructedchoice_vbox is choice_vbox:
    xcenter 1050

style unobstructedchoice_button is choice_button

style unobstructedchoice_button_dark is choice_button_dark

style unobstructedchoice_button_text is choice_button_text

style unobstructedchoice_button_text_dark is choice_button_text_dark
