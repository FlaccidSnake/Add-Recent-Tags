from aqt import mw, gui_hooks
from aqt.qt import QMenu, QAction
from aqt.utils import qconnect
from aqt.webview import AnkiWebView, AnkiWebViewKind
from .recent_tags_dialog import RecentTagsDialog


def get_config():
    """Get addon configuration."""
    return mw.addonManager.getConfig(__name__)


def get_recent_tags(limit=None):
    """Get tags from the most recently added notes."""
    if limit is None:
        config = get_config()
        limit = config.get("number_of_tags", 5)
    
    # Get search depth from config
    search_limit = config.get("search_depth", 50) if limit else 50
    
    # Get all note IDs sorted by ID (which corresponds to creation time)
    # Use direct database query to get most recent notes
    note_ids = mw.col.db.list(
        "SELECT id FROM notes ORDER BY id DESC LIMIT ?", 
        search_limit
    )
    
    recent_tags = []
    seen_tags = set()
    
    for nid in note_ids:
        note = mw.col.get_note(nid)
        for tag in note.tags:
            if tag not in seen_tags:
                recent_tags.append(tag)
                seen_tags.add(tag)
                if len(recent_tags) >= limit:
                    return recent_tags
    
    return recent_tags


def add_tags_to_notes(note_ids, tags_to_add):
    """Add tags to the specified notes."""
    if not tags_to_add:
        return
    
    mw.checkpoint("Add Recent Tags")
    for nid in note_ids:
        note = mw.col.get_note(nid)
        for tag in tags_to_add:
            if tag and tag not in note.tags:
                note.tags.append(tag)
        mw.col.update_note(note)
    mw.reset()


# Browser context menu
def on_browser_context_menu(browser, menu):
    """Add 'Add recent tags' to browser context menu."""
    selected_nids = browser.selected_notes()
    if not selected_nids:
        return
    
    # Get all actions
    actions = menu.actions()
    
    # Create our action
    recent_tags_action = QAction("Add Recent Tags", menu)
    qconnect(recent_tags_action.triggered, lambda: show_recent_tags_dialog(browser, selected_nids))
    
    # Insert as 5th item (index 4) - right after typical "Add Tags" position
    # If menu has fewer items, it will be added at the end
    if len(actions) >= 5:
        menu.insertAction(actions[4], recent_tags_action)
    elif len(actions) >= 1:
        # Try to find "Add Tags" or similar and insert after it
        insert_position = None
        for i, action in enumerate(actions):
            action_text = action.text().lower()
            if "add tags" in action_text or "tags" in action_text:
                insert_position = i + 1
                break
        
        if insert_position is not None and insert_position < len(actions):
            menu.insertAction(actions[insert_position], recent_tags_action)
        else:
            menu.addAction(recent_tags_action)
    else:
        menu.addAction(recent_tags_action)


def show_recent_tags_dialog(parent, note_ids):
    """Show the recent tags dialog."""
    recent_tags = get_recent_tags()
    if not recent_tags:
        from aqt.utils import tooltip
        tooltip("No recent tags found")
        return
    
    dialog = RecentTagsDialog(parent, recent_tags)
    if dialog.exec():
        selected_tags = dialog.get_selected_tags()
        add_tags_to_notes(note_ids, selected_tags)
        from aqt.utils import tooltip
        tooltip(f"Added {len(selected_tags)} tag(s) to {len(note_ids)} note(s)")


# Editor sidebar context menu
def on_editor_context_menu(editor_web_view, menu):
    """Add 'Add recent tags' to editor sidebar context menu."""
    editor = editor_web_view.editor
    if not editor.note:
        return
    
    action = menu.addAction("Add Recent Tags")
    qconnect(action.triggered, lambda: show_recent_tags_dialog(
        editor.parentWindow, [editor.note.id]))


# Reviewer context menu (webview)
def on_webview_context_menu(webview: AnkiWebView, menu: QMenu):
    """Add 'Add recent tags' to reviewer webview context menu."""
    if mw.state != 'review' or not webview.kind == AnkiWebViewKind.MAIN:
        return
    
    if not mw.reviewer.card:
        return
    
    note_id = mw.reviewer.card.nid
    
    # Get all actions
    actions = menu.actions()
    
    # Create our action
    recent_tags_action = QAction("Add Recent Tags", menu)
    qconnect(recent_tags_action.triggered, lambda: show_recent_tags_dialog(mw, [note_id]))
    
    # Insert at position 5 or find appropriate position
    if len(actions) >= 5:
        menu.insertAction(actions[4], recent_tags_action)
    else:
        menu.addAction(recent_tags_action)


# Reviewer context menu (more menu button)
def on_reviewer_context_menu(reviewer, menu):
    """Add 'Add recent tags' to reviewer more menu."""
    if mw.state != 'review':
        return
    
    if not reviewer.card:
        return
    
    note_id = reviewer.card.nid
    
    # Get all actions
    actions = menu.actions()
    
    # Create our action
    recent_tags_action = QAction("Add Recent Tags", menu)
    qconnect(recent_tags_action.triggered, lambda: show_recent_tags_dialog(
        reviewer.mw, [note_id]))
    
    # Insert at position 5 or find appropriate position
    if len(actions) >= 5:
        menu.insertAction(actions[4], recent_tags_action)
    else:
        menu.addAction(recent_tags_action)


# Register hooks
gui_hooks.browser_will_show_context_menu.append(on_browser_context_menu)
gui_hooks.editor_will_show_context_menu.append(on_editor_context_menu)
gui_hooks.webview_will_show_context_menu.append(on_webview_context_menu)
gui_hooks.reviewer_will_show_context_menu.append(on_reviewer_context_menu)