"""Tests for structural pattern matching (PEP-634)."""

from pytype.tests import test_base
from pytype.tests import test_utils


@test_utils.skipBeforePy((3, 10), "New syntax in 3.10")
class MatchTest(test_base.BaseTest):
  """Test match statement for builtin datatypes."""

  def test_basic(self):
    ty = self.Infer("""
      def f(x):
        match x:
          case 1:
            return 'a'
          case 2:
            return 10
    """)
    self.assertTypesMatchPytd(ty, """
      def f(x) -> int | str | None: ...
    """)

  def test_default(self):
    ty = self.Infer("""
      def f(x):
        match x:
          case 1:
            return 'a'
          case 2:
            return 10
          case _:
            return 20
    """)
    self.assertTypesMatchPytd(ty, """
      def f(x) -> int | str: ...
    """)

  def test_sequence1(self):
    ty = self.Infer("""
      def f(x):
        match x:
          case [a]:
            return a
    """)
    self.assertTypesMatchPytd(ty, """
      from typing import Any
      def f(x) -> Any: ...
    """)

  def test_sequence2(self):
    ty = self.Infer("""
      def f(x: int):
        match x:
          case [a]:
            return a
    """)
    self.assertTypesMatchPytd(ty, """
      def f(x: int) -> None: ...
    """)

  def test_list1(self):
    ty = self.Infer("""
      def f(x: list[int]):
        match x:
          case [a]:
            return a
    """)
    self.assertTypesMatchPytd(ty, """
      def f(x: list[int]) -> int | None: ...
    """)

  def test_list2(self):
    ty = self.Infer("""
      def f(x: list[int]):
        match x:
          case [a]:
            return a
          case [a, *rest]:
            return rest
    """)
    self.assertTypesMatchPytd(ty, """
      def f(x: list[int]) -> int | list[int] | None: ...
    """)

  @test_base.skip("Exhaustiveness checks not implemented")
  def test_list3(self):
    ty = self.Infer("""
      def f(x: list[int]):
        match x:
          case []:
            return 0
          case [a]:
            return a
          case [a, *rest]:
            return rest
    """)
    self.assertTypesMatchPytd(ty, """
      def f(x: list[int]) -> int | list[int]: ...
    """)

  def test_list4(self):
    ty = self.Infer("""
      def f(x: list[int]):
        match x:
          case [*all]:
            return 0
          case _:
            return '1'
    """)
    self.assertTypesMatchPytd(ty, """
      def f(x: list[int]) -> int: ...
    """)

  def test_tuple(self):
    ty = self.Infer("""
      def f(x: tuple[int, str]):
        match x:
          case [a, b]:
            return b
    """)
    self.assertTypesMatchPytd(ty, """
      def f(x: tuple[int, str]) -> str: ...
    """)

  def test_tuple2(self):
    ty = self.Infer("""
      def f(x: tuple[int, str]):
        match x:
          case [a, b, *rest]:
            return b
    """)
    self.assertTypesMatchPytd(ty, """
      def f(x: tuple[int, str]) -> str: ...
    """)

  def test_map1(self):
    ty = self.Infer("""
      def f(x):
        match x:
          case {'x': a}:
            return 0
          case {'y': b}:
            return '1'
    """)
    self.assertTypesMatchPytd(ty, """
      def f(x) -> int | str | None : ...
    """)

  def test_map2(self):
    ty = self.Infer("""
      def f(x):
        match x:
          case {'x': a}:
            return a
          case {'y': b}:
            return b
    """)
    self.assertTypesMatchPytd(ty, """
      from typing import Any
      def f(x) -> Any: ...
    """)

  def test_map3(self):
    ty = self.Infer("""
      def f():
        x = {'x': 1, 'y': '2'}
        match x:
          case {'x': a}:
            return a
          case {'y': b}:
            return b
    """)
    self.assertTypesMatchPytd(ty, """
      def f() -> int: ...
    """)


@test_utils.skipBeforePy((3, 10), "New syntax in 3.10")
class MatchClassTest(test_base.BaseTest):
  """Test match statement for classes."""

  def test_unknown(self):
    ty = self.Infer("""
      class A:
        x: int = ...
        y: str = ...
      def f(x):
        match x:
          case A(x=a, y=b):
            return b
          case _:
            return 42
    """)
    self.assertTypesMatchPytd(ty, """
      class A:
        x: int
        y: str

      def f(x) -> int | str: ...
    """)

  def test_annotated(self):
    ty = self.Infer("""
      class A:
        x: int = ...
        y: str = ...
      def f(x: A):
        match x:
          case A(x=a, y=b):
            return b
          case _:
            return 42
    """)
    self.assertTypesMatchPytd(ty, """
      class A:
        x: int
        y: str

      def f(x: A) -> str: ...
    """)

  def test_instance1(self):
    ty = self.Infer("""
      class A:
        def __init__(self, x: int, y: str):
          self.x = x
          self.y = y

      def f():
        x = A(1, '2')
        match x:
          case A(x=a, y=b):
            return b
          case _:
            return 42
    """)
    self.assertTypesMatchPytd(ty, """
      class A:
        x: int
        y: str
        def __init__(self, x: int, y: str) -> None: ...

      def f() -> str: ...
    """)

  def test_instance2(self):
    ty = self.Infer("""
      class A:
        def __init__(self, x):
          self.x = x
      def f(x):
        match x:
          case A(x=a):
            return a
          case _:
            return False
      a = f(A(10))
      b = f(A('20'))
      c = f('foo')
    """)
    self.assertTypesMatchPytd(ty, """
      from typing import Any
      class A:
        x: Any
        def __init__(self, x) -> None: ...

      def f(x) -> Any: ...
      a: int
      b: str
      c: bool
    """)


if __name__ == "__main__":
  test_base.main()
