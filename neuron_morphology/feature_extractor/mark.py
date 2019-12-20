from typing import Callable, Set


from neuron_morphology.morphology import Morphology


class Mark:

    def applicable(self, morphology: Morphology) -> bool:
        return True


class RequiresLayerAnnotations(Mark):

    def applicable(self, morphology):

        has_layers = True
        for node in morphology.nodes:
            has_layers = has_layers and "layer" in node
            if not has_layers:
                break

        return has_layers


class MarkedFn:

    __slots__ = ["marks", "fn", "name"]

    def __init__(self, marks: Set[Mark], fn: Callable):
        self.marks = marks
        self.fn = fn
        
        if hasattr(fn, "name"):
            self.name = fn.name
        else:
            self.name = fn.__name__

    def add_mark(self, mark: Mark):
        self.marks.add(mark)

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)


def marked(mark):

    def _add_mark(fn):

        if hasattr(fn, "marks"):
            fn.marks.add(mark)
        else:
            fn = MarkedFn(set([mark]), fn)

        return fn

    return _add_mark


if __name__ == "__main__":

    @marked(RequiresLayerAnnotations)
    def foo():
        print("hi")

    print(foo.marks, foo.marks == set([RequiresLayerAnnotations]))