import unittest

import chainer
from chainer import testing
from chainer.testing import attr

from chainercv.links import DeepLabV3plusXception65
from chainercv.utils import assert_is_semantic_segmentation_link

import numpy as np


@testing.parameterize(
    {'model': DeepLabV3plusXception65},
)
class TestDeepLabV3plusXception65(unittest.TestCase):

    def setUp(self):
        self.n_class = 10
        self.link = self.model(n_class=self.n_class)

    def check_call(self):
        xp = self.link.xp
        h, w = 120, 160
        x = chainer.Variable(xp.random.uniform(
            low=-1, high=1, size=(2, 3, h, w)).astype(np.float32))
        y = self.link(x)

        self.assertIsInstance(y, chainer.Variable)
        self.assertIsInstance(y.data, xp.ndarray)
        self.assertEqual(y.shape, (2, self.n_class, h // 4, w // 4))

    @attr.slow
    def test_call_cpu(self):
        self.check_call()

    @attr.gpu
    @attr.slow
    def test_call_gpu(self):
        self.link.to_gpu()
        self.check_call()

    @attr.slow
    def test_predict_cpu(self):
        assert_is_semantic_segmentation_link(self.link, self.n_class)

    @attr.gpu
    @attr.slow
    def test_predict_gpu(self):
        self.link.to_gpu()
        assert_is_semantic_segmentation_link(self.link, self.n_class)


@testing.parameterize(*testing.product({
    'model': [DeepLabV3plusXception65],
    'pretrained_model': ['cityscapes', 'ade20k', 'voc'],
    'n_class': [None, 19, 150, 21],
}))
class TestDeepLabV3plusXception65Pretrained(unittest.TestCase):

    @attr.slow
    def test_pretrained(self):
        kwargs = {
            'n_class': self.n_class,
            'pretrained_model': self.pretrained_model,
        }

        if self.pretrained_model == 'cityscapes':
            valid = self.n_class in {None, 19}
        elif self.pretrained_model == 'ade20k':
            valid = self.n_class in {None, 150}
        elif self.pretrained_model == 'voc':
            valid = self.n_class in {None, 21}

        if valid:
            self.model(**kwargs)
        else:
            with self.assertRaises(ValueError):
                self.model(**kwargs)


testing.run_module(__name__, __file__)
