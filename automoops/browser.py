_page = None
_context = None


def set_browser(context, page):
    global _context, _page
    _context = context
    _page = page


def get_page():
    return _page


def get_context():
    return _context
