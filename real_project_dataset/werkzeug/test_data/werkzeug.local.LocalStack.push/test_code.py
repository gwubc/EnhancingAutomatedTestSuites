def test_local_release():
    ns = local.Local(_cv_ns)
    ns.foo = 42
    local.release_local(ns)
    assert not hasattr(ns, "foo")
    ls = local.LocalStack(_cv_stack)
    ls.push(42)
    local.release_local(ls)
    assert ls.top is None

def test_local_stack():
    ls = local.LocalStack(_cv_stack)
    assert ls.top is None
    ls.push(42)
    assert ls.top == 42
    ls.push(23)
    assert ls.top == 23
    ls.pop()
    assert ls.top == 42
    ls.pop()
    assert ls.top is None
    assert ls.pop() is None
    assert ls.pop() is None
    proxy = ls()
    ls.push([1, 2])
    assert proxy == [1, 2]
    ls.push((1, 2))
    assert proxy == (1, 2)
    ls.pop()
    ls.pop()
    assert repr(proxy) == "<LocalProxy unbound>"

def test_local_stack_asyncio():
    ls = local.LocalStack(_cv_stack)
    ls.push(1)

    async def task():
        ls.push(1)
        assert len(ls._storage.get()) == 2

    async def main():
        futures = [asyncio.ensure_future(task()) for _ in range(3)]
        await asyncio.gather(*futures)

    asyncio.run(main())

async def task():
        ls.push(1)
        assert len(ls._storage.get()) == 2

def test_proxy_fallback():
    local_stack = local.LocalStack(_cv_stack)
    local_proxy = local_stack()
    assert repr(local_proxy) == "<LocalProxy unbound>"
    assert isinstance(local_proxy, local.LocalProxy)
    assert local_proxy.__class__ is local.LocalProxy
    assert "LocalProxy" in local_proxy.__doc__
    local_stack.push(42)
    assert repr(local_proxy) == "42"
    assert isinstance(local_proxy, int)
    assert local_proxy.__class__ is int
    assert "int(" in local_proxy.__doc__