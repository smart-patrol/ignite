from ignite.metrics import EpochMetric
import torch
import pytest


def test_epoch_metric():

    def compute_fn(y_preds, y_targets):
        return 0.0

    em = EpochMetric(compute_fn)

    # Wrong input dims
    with pytest.raises(AssertionError):
        output = (torch.tensor(0), torch.tensor(0))
        em.update(output)

    # Wrong input dims
    with pytest.raises(AssertionError):
        output = (torch.rand(4, 3, 1), torch.rand(4, 3))
        em.update(output)

    # Target is not binary
    with pytest.raises(AssertionError):
        output = (torch.rand(4, 3), torch.randint(0, 5, size=(4, 3)))
        em.update(output)

    em.reset()
    output1 = (torch.rand(4, 3), torch.randint(0, 2, size=(4, 3), dtype=torch.long))
    em.update(output1)
    output2 = (torch.rand(4, 3), torch.randint(0, 2, size=(4, 3), dtype=torch.long))
    em.update(output2)

    assert em._predictions.device.type == 'cpu' and em._targets.device.type == 'cpu'
    assert torch.equal(em._predictions[:4, :], output1[0])
    assert torch.equal(em._predictions[4:, :], output2[0])
    assert torch.equal(em._targets[:4, :], output1[1])
    assert torch.equal(em._targets[4:, :], output2[1])
    assert em.compute() == 0.0


def test_mse_epoch_metric():

    def compute_fn(y_preds, y_targets):
        return torch.mean(((y_preds - y_targets.type_as(y_preds)) ** 2)).item()

    em = EpochMetric(compute_fn)

    em.reset()
    output1 = (torch.rand(4, 3), torch.randint(0, 2, size=(4, 3), dtype=torch.long))
    em.update(output1)
    output2 = (torch.rand(4, 3), torch.randint(0, 2, size=(4, 3), dtype=torch.long))
    em.update(output2)
    output3 = (torch.rand(4, 3), torch.randint(0, 2, size=(4, 3), dtype=torch.long))
    em.update(output3)

    preds = torch.cat([output1[0], output2[0], output3[0]], dim=0)
    targets = torch.cat([output1[1], output2[1], output3[1]], dim=0)

    result = em.compute()
    assert result == compute_fn(preds, targets)

    em.reset()
    output1 = (torch.rand(4, 3), torch.randint(0, 2, size=(4, 3), dtype=torch.long))
    em.update(output1)
    output2 = (torch.rand(4, 3), torch.randint(0, 2, size=(4, 3), dtype=torch.long))
    em.update(output2)
    output3 = (torch.rand(4, 3), torch.randint(0, 2, size=(4, 3), dtype=torch.long))
    em.update(output3)

    preds = torch.cat([output1[0], output2[0], output3[0]], dim=0)
    targets = torch.cat([output1[1], output2[1], output3[1]], dim=0)

    result = em.compute()
    assert result == compute_fn(preds, targets)


def test_bad_compute_fn():

    def compute_fn(y_preds, y_targets):
        # Following will raise the error: Expected object of type torch.FloatTensor but found type
        # torch.LongTensor for argument #3 'other'
        return torch.mean(y_preds - y_targets).item()

    em = EpochMetric(compute_fn)

    em.reset()
    output1 = (torch.rand(4, 3), torch.randint(0, 2, size=(4, 3), dtype=torch.long))
    with pytest.raises(RuntimeError):
        em.update(output1)
