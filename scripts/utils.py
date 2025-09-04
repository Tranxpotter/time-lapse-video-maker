import pygame_gui

def scroll_to_index(selection_list:pygame_gui.elements.UISelectionList, index, items_displayed:int = 30):
    total_items = len(selection_list.item_list)
    if total_items > 1:
        scroll_pos = (index-items_displayed//2) / (total_items - 1)
        if scroll_pos > 1:
            scroll_pos = 1.0
        if scroll_pos < 0:
            scroll_pos = 0.0
        if selection_list.scroll_bar:
            selection_list.scroll_bar.set_scroll_from_start_percentage(scroll_pos)
    else:
        if selection_list.scroll_bar:
            selection_list.scroll_bar.set_scroll_from_start_percentage(0.0)