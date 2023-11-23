class TransferFunction(object):

    def __init__(self, nominator_list: list[float], denominator_list: list[float]):
        """
        Инициализация передаточной функции.

        :param nominator_list: Список из коэффициентов числителя.
        :param denominator_list: Список из коэффициентов знаменателя.
        """
        self.nominator_list = nominator_list
        self.denominator_list = denominator_list

    def evaluate(self, p: float) -> float:
        """
        Вычислить значение передаточной функции в точке.

        :param p: Точка, в которой будет произведено вычисление.
        :return: Значение передаточной функции в точке p.
        """
        nominator_val = 0.0
        nominator_len = len(self.nominator_list)

        for i in range(nominator_len):
            nominator_val += self.nominator_list[i] * (p ** (nominator_len - 1 - i))

        denominator_val = 0.0
        denominator_len = len(self.denominator_list)

        for i in range(denominator_len):
            denominator_val += self.denominator_list[i] * (p ** (denominator_len - 1 - i))

        return nominator_val / denominator_val

    def get_coefficients(self) -> tuple[list[float], list[float]]:
        """
        Возвращает коэффициенты передаточной функции.

        :return: Кортеж, содержащий два списка: с коэффициентами числителя и с коэффициентами знаменателя передаточной функции.
        """
        return self.nominator_list, self.denominator_list
