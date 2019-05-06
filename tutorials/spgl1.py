r"""
SPGL1 Tutorial
==============
In this tutorial we will explore the different solvers in the ``spgl1``
package and apply them to different toy examples.
"""
import numpy as np
import matplotlib.pyplot as plt

from scipy.sparse.linalg import LinearOperator
from scipy.sparse import spdiags
import spgl1

# Initialize random number generators
np.random.seed(43273289)

###############################################################################
# Create random m-by-n encoding matrix and sparse vector
m = 50
n = 128
k = 14
[A,Rtmp] = np.linalg.qr(np.random.randn(n,m),'reduced')
A  = A.T
p  = np.random.permutation(n)
p = p[0:k]
x0 = np.zeros(n)
x0[p] = np.random.randn(k)

###############################################################################
# Solve the underdetermined LASSO problem for :math:`||x||_1 <= \pi`:
#
# .. math::
#   min.||Ax-b||_2 \quad subject \quad  to \quad ||x||_1 <= \pi
b = A.dot(x0)
tau = np.pi
x,resid,grad,info = spgl1.spg_lasso(A, b, tau, verbosity=1)

print('%s%s%s' % ('-'*35,' Solution ','-'*35))
print('nonzeros(x) = %i,   ||x||_1 = %12.6e,   ||x||_1 - pi = %13.6e' %
      (np.sum(abs(x)>1e-5), np.linalg.norm(x,1), np.linalg.norm(x,1)-np.pi))
print('%s' % ('-'*80))

###############################################################################
# Solve the basis pursuit (BP) problem:
# .. math::
#     min.  ||x||_1 \quad subject \quad  to \quad  Ax = b
b = A.dot(x0)
x,resid,grad,info = spgl1.spg_bp(A, b, verbosity=2)

plt.figure()
plt.plot(x,'b')
plt.plot(x0,'ro')
plt.legend(('Recovered coefficients','Original coefficients'))
plt.title('(a) Basis Pursuit')

plt.figure()
plt.plot(info['xNorm1'], info['rNorm2'], '.-k')
plt.xlabel(r'$||x||_1$')
plt.ylabel(r'$||r||_2$')
plt.title('Pareto curve')

plt.figure()
plt.plot(np.arange(info['iterr']), info['rNorm2']/max(info['rNorm2']),
         '.-k', label=r'$||r||_2$')
plt.plot(np.arange(info['iterr']), info['xNorm1']/max(info['xNorm1']),
         '.-r', label=r'$||x||_1$')
plt.xlabel(r'#iter')
plt.ylabel(r'$||r||_2/||x||_1$')
plt.title('Norms')
plt.legend()

###############################################################################
# Solve the basis pursuit denoise (BPDN) problem:
# .. math::
#     min. ||x||_1 \quad subject \quad to \quad ||Ax - b||_2 <= 0.1

b = A.dot(x0) + np.random.randn(m) * 0.075
sigma = 0.10  #     % Desired ||Ax - b||_2
x, resid, grad, info = spgl1.spg_bpdn(A, b, sigma, iterations=10, verbosity=2)

plt.figure()
plt.plot(x,'b')
plt.plot(x0,'ro')
plt.legend(('Recovered coefficients','Original coefficients'))
plt.title('(b) Basis Pursuit Denoise')

###############################################################################
# Solve the basis pursuit (BP) problem in complex variables:
# .. math::
#   min. ||z||_1 \quad subject \quad to \quad  Az = b$$
class partialFourier(LinearOperator):
    def __init__(self, idx, n):
        self.idx = idx
        self.n = n
        self.shape = (len(idx), n)
        self.dtype = np.complex128
    def _matvec(self, x):
        # % y = P(idx) * FFT(x)
        z = np.fft.fft(x) / np.sqrt(n)
        return z[idx]
    def _rmatvec(self, x):
        z = np.zeros(n,dtype=complex)
        z[idx] = x
        return np.fft.ifft(z) * np.sqrt(n)


# % Create partial Fourier operator with rows idx
idx = np.random.permutation(n)
idx = idx[0:m]
opA = partialFourier(idx, n)

# % Create sparse coefficients and b = 'A' * z0;
z0 = np.zeros(n,dtype=complex)
z0[p] = np.random.randn(k) + 1j * np.random.randn(k)
b = opA.matvec(z0)

z, resid, grad, info = spgl1.spg_bp(opA, b, verbosity=2)

plt.figure()
plt.plot(z.real,'b+',markersize=15.0)
plt.plot(z0.real,'bo')
plt.plot(z.imag,'r+',markersize=15.0)
plt.plot(z0.imag,'ro')
plt.legend(('Recovered (real)', 'Original (real)',
            'Recovered (imag)', 'Original (imag)'))
plt.title('(c) Complex Basis Pursuit')