class TransferFunction(object):
    @staticmethod
    def w(p, a0=0, a1=0, a2=0, a3=0, a4=0, a5=0, a6=0, a7=0, b0=0, b1=0, b2=0, b3=0, b4=0, b5=0, b6=0, b7=0):
        return (a7 * p ** 7 + a6 * p ** 6 + a5 * p ** 5 + a4 * p ** 4 + a3 * p ** 3 + a2 * p ** 2 + a1 * p + a0) / \
               (b7 * p ** 7 + b6 * p ** 6 + b5 * p ** 5 + b4 * p ** 4 + b3 * p ** 3 + b2 * p ** 2 + b1 * p + b0)
