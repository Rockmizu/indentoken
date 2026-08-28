from __future__ import annotations

from typing import Final

# The method rely on CPython implementation detail to work and should
# only been re-implemented when PEP 533
# Deterministic cleanup for iterators becomes available.
INDENTOKEN_ENABLE_IT_METHOD: Final = False
