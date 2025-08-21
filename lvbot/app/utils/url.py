from urllib.parse import urlparse, urlunparse

def to_public(url: str, public_base: str) -> str:
    """
    Приводит любые ссылки (полные/относительные/внутренние) к публичному базовому хосту.
    Пример:
      url='http://backend:8000/media/x.zip', public='https://lavrpro.ru'
      -> 'https://lavrpro.ru/media/x.zip'
    """
    if not url:
        return url

    pb = public_base.rstrip("/")
    if not pb.startswith(("http://", "https://")):
        pb = "https://" + pb  # телеге лучше https

    base = urlparse(pb)

    # относительный путь
    if url.startswith("/"):
        return f"{base.scheme}://{base.netloc}{url}"

    p = urlparse(url)

    # без netloc (типа 'media/x.zip')
    if not p.netloc:
        path = "/" + url.lstrip("/")
        return f"{base.scheme}://{base.netloc}{path}"

    # абсолютный, но внутренний — заменяем схему+хост
    new = p._replace(scheme=base.scheme, netloc=base.netloc)
    return urlunparse(new)