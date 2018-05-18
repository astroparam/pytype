"""Tests for slots."""

from pytype.tests import test_base


class SlotsTest(test_base.TargetPython3FeatureTest):
  """Tests for __slots__."""

  def testSlotWithUnicode(self):
    self.Check("""
      class Foo(object):
        __slots__ = (u"fo\\xf6", u"b\\xe4r", "baz")
      Foo().baz = 3
    """)

  def testSlotWithBytes(self):
    errors = self.CheckWithErrors("""\
      class Foo(object):
        __slots__ = (b"x",)
    """)
    self.assertErrorLogIs(errors, [(1, "bad-slots")])


test_base.main(globals(), __name__ == "__main__")
