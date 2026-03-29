"""TaskMaster application package."""

__version__ = "0.1.2"

def setup_logging():
	"""Apply minimal logging configuration for the application."""
	import logging
	handler = logging.StreamHandler()
	formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
	handler.setFormatter(formatter)
	root = logging.getLogger()
	if not root.handlers:
		root.addHandler(handler)
		root.setLevel(logging.INFO)

setup_logging()
