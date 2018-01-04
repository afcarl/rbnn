import math
import torch
import h5py
import numpy as np

# def logsum_mog(x, pi, mu1, mu2, sigma1, sigma2):
#     return log_sum_exp(torch.log(pi) + log_normal(x, mu1, sigma1),
#                        torch.log(1. - pi) + log_normal(x, mu2, sigma2))


# def log_sum_exp(u, v):
#     m = torch.maximum(u, v)
#     return m + torch.log(torch.exp(u - m) + torch.exp(v - m))


# def log_normal(x, mu, sigma):
#     return -0.5 * torch.log(2.0 * math.pi) - torch.log(torch.abs(sigma)) - torch.pow(x - mu, 2) / (
#         2. * torch.pow(sigma, 2))


def logsumexp(x, dim):
    """Logsumexp trick to avoid overflow in a log of sum of exponential expression

    Args:
        x (Variable or Tensor): the input on which to compute the log of sum of exponential

    Returns:
        logsum (Variable or Tensor): the computed log of sum of exponential
    """

    assert x.dim() == 2
    x_max, x_max_idx = x.max(dim=dim, keepdim=True)
    logsum = x_max + torch.log((x - x_max).exp().sum(dim=dim, keepdim=True))
    return logsum


# def compute_KL_bis(x, mu, sigma, prior_sigma1, prior_sigma2, prior_pi):
#     # INCORRECT IMPLEMENTATION ?
#     """
#     Compute KL divergence between posterior and prior.
#     """
#     posterior = torch.distributions.Normal(mu, sigma)
#     KL = torch.sum(posterior.log_prob(x))

#     prior1 = torch.distributions.Normal(0.0, prior_sigma1)
#     prior2 = torch.distributions.Normal(0.0, prior_sigma2)

#     mix1 = torch.sum(prior1.log_prob(x)) + math.log(prior_pi)
#     mix2 = torch.sum(prior2.log_prob(x)) + math.log(1.0 - prior_pi)
#     prior_mix = torch.stack([mix1, mix2], dim=-1)
#     KL += -torch.sum(logsumexp(prior_mix))
#     return KL


# def compute_KL_bis_logsumexp(x, mu, sigma, prior_sigma1, prior_sigma2, prior_pi):
#     """
#     Compute KL divergence between posterior and prior.
#     """

#     posterior = torch.distributions.Normal(mu, sigma)
#     log_posterior = posterior.log_prob(x).sum()

#     N1 = torch.distributions.Normal(0.0, prior_sigma1)
#     N2 = torch.distributions.Normal(0.0, prior_sigma2)

#     prior1 = math.log(prior_pi) + N1.log_prob(x)
#     prior2 = math.log(1.0 - prior_pi) + N2.log_prob(x)

#     prior = torch.stack([prior1, prior2], -1)
#     try:
#         log_prior = logsumexp(prior).sum()
#     except RuntimeError:
#         import ipdb
#         ipdb.set_trace()
#     return log_posterior - log_prior


def compute_KL(x, mu, sigma, prior):
    """
    Compute KL divergence between posterior and prior.
    """

    posterior = torch.distributions.Normal(mu, sigma)
    log_posterior = posterior.log_prob(x).sum()

    N1 = torch.distributions.Normal(0.0, prior.sigma1)
    N2 = torch.distributions.Normal(0.0, prior.sigma2)

    prior1 = prior.pi_mixture * N1.log_prob(x).exp()
    prior2 = (1.0 - prior.pi_mixture) * N2.log_prob(x).exp()

    prior = prior1 + prior2
    log_prior = prior.log().sum()

    return log_posterior - log_prior


# def compute_KL(sample, mu, sigma, prior):
#     """
#     Compute KL divergence between posterior and prior.
#     """

#     # import ipdb; ipdb.set_trace()

#     posterior = torch.distributions.Normal(mu, sigma)
#     posterior = torch.sum(posterior.log_prob(sample.view(-1)))
#     N1 = torch.distributions.Normal(0.0, prior.sigma1)
#     N2 = torch.distributions.Normal(0.0, prior.sigma2)
#     mix1 = torch.sum(N1.log_prob(sample), 1) + math.log(prior.pi_mixture)
#     mix2 = torch.sum(N2.log_prob(sample), 1) + math.log(1.0 - prior.pi_mixture)
#     prior_mix = torch.stack([mix1, mix2])
#     prior = torch.sum(logsumexp(prior_mix, 0))

#     KL = posterior - prior

#     # with h5py.File("weights.h5", "r") as hf:
#     #     tf_post = np.array(hf["kl_emb_posterior"])
#     #     tf_pri = np.array(hf["kl_emb_prior"])

#     # det = - math.log(math.sqrt(2 * math.pi)) - sigma.log()
#     # exp = -0.5 * ((sample.view(-1) - mu) / sigma).pow(2)
#     # mypost = (exp + det).sum()

#     # import ipdb; ipdb.set_trace()

#     return KL
