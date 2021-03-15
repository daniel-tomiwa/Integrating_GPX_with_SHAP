import numpy as np
from scipy.spatial import distance


class NoiseSet:

    def __init__(self, explainer) -> None:
        self.xpr = explainer

    def create_noise_set(self, instance):
        """
        Create a noise set around a instance that will be explain

        :param instance: numpy array with size equals to number of features in problem.
        :return: x, y created around instance (y is predict by a black box model)
        """

        d = len(instance)
        x_created = np.random.normal(instance, scale=self.xpr.x_train_measure, size=(self.xpr.num_samples, d))
        y_created = self.xpr.predict(x_created)

        if self.xpr.problem == 'regression':

            return x_created, y_created

        else:

            y_min = np.min(y_created)
            y_max = np.max(y_created)

            if y_max != y_min:

                return x_created, y_created

            else:

                i_want = np.where(self.xpr.y_train != y_max)[0]
                x_other_class = self.xpr.x_train[i_want, :]
                cut = np.floor(self.xpr.num_samples * .2)
                cut = int(cut)
                x_created = np.concatenate((x_created, x_other_class[:cut, :]), axis=0)
                y_created = self.xpr.predict(x_created)

                return x_created, y_created

    def noise_set(self, instance):
        """
        Create a noise set around a instance that will be explain

        :param instance: numpy array with size equals to number of features in problem.
        :return: x, y created around instance (y is predict by a black box model predict)
        """

        d = len(instance)
        x_created = np.random.normal(instance, scale=self.xpr.x_train_measure, size=(self.xpr.num_samples, d))
        y_created = self.xpr.predict(x_created)

        return x_created, y_created

    def noise_k_neighbor(self, instance, k):

        y_my = self.xpr.y_train.reshape(-1)

        each_class = {label: self.xpr.x_train[y_my == label, :] for label in self.xpr.labels}
        each_distance = {label: distance.cdist(my_class, instance.reshape(1, -1))
                         for label, my_class in each_class.items()}
        k_distance = {label: np.argsort(dist_class, axis=0)[:k] for label, dist_class in each_distance.items()}
        k_neighbor = {label: each_class[label][idx][:, 0] for label, idx in k_distance.items()}

        noise_set = np.concatenate(tuple(k_neighbor.values()), axis=0)

        x_created = self.xpr.max_min_matrix(noise_set,
                                        noise_range=self.xpr.num_samples,
                                        dist_type='uniform')

        x_created = np.append(x_created, noise_set, axis=0)

        y_created = self.xpr.predict(x_created)

        return x_created, y_created, k_neighbor, k_distance, each_distance, each_class

    def generate_data_around(self, instance):
        if self.xpr.k_neighbor is not None and self.xpr.problem == 'classification':
            x_around, y_around, _, _, _, _ = self.noise_k_neighbor(instance, self.xpr.k_neighbor)
            return x_around, y_around
        else:
            return self.noise_set(instance)

