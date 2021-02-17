import torch 
import torch.nn as nn
import torchvision.models as models
import torchvision
import os, sys

if __name__ == '__main__':
    sys.path.append(os.getcwd())
sys.path[0]=os.path.dirname(os.path.realpath(__file__))


PYTORCH_VGG_KEYS = ["features.0.weight", "features.0.bias", "features.2.weight", "features.2.bias", "features.5.weight", "features.5.bias", "features.7.weight", "features.7.bias", "features.10.weight", "features.10.bias", "features.12.weight", "features.12.bias", "features.14.weight", "features.14.bias", "features.17.weight", "features.17.bias", "features.19.weight", "features.19.bias", "features.21.weight", "features.21.bias", "features.24.weight", "features.24.bias", "features.26.weight", "features.26.bias", "features.28.weight", "features.28.bias", "classifier.0.weight", "classifier.0.bias", "classifier.3.weight", "classifier.3.bias", "classifier.6.weight", "classifier.6.bias"]
VGG_FACE_DAG_KEYS = ["conv1_1.weight", "conv1_1.bias", "conv1_2.weight", "conv1_2.bias", "conv2_1.weight", "conv2_1.bias", "conv2_2.weight", "conv2_2.bias", "conv3_1.weight", "conv3_1.bias", "conv3_2.weight", "conv3_2.bias", "conv3_3.weight", "conv3_3.bias", "conv4_1.weight", "conv4_1.bias", "conv4_2.weight", "conv4_2.bias", "conv4_3.weight", "conv4_3.bias", "conv5_1.weight", "conv5_1.bias", "conv5_2.weight", "conv5_2.bias", "conv5_3.weight", "conv5_3.bias", "fc6.weight", "fc6.bias", "fc7.weight", "fc7.bias", "fc8.weight", "fc8.bias"]
PREFIXED_KEYS = ["0.features.0.weight", "0.features.0.bias", "0.features.2.weight", "0.features.2.bias", "0.features.5.weight", "0.features.5.bias", "0.features.7.weight", "0.features.7.bias", "0.features.10.weight", "0.features.10.bias", "0.features.12.weight", "0.features.12.bias", "0.features.14.weight", "0.features.14.bias", "0.features.17.weight", "0.features.17.bias", "0.features.19.weight", "0.features.19.bias", "0.features.21.weight", "0.features.21.bias", "0.features.24.weight", "0.features.24.bias", "0.features.26.weight", "0.features.26.bias", "0.features.28.weight", "0.features.28.bias", "0.classifier.0.weight", "0.classifier.0.bias", "0.classifier.3.weight", "0.classifier.3.bias", "0.classifier.6.weight", "0.classifier.6.bias"]


class MaskedFaceVgg(nn.Module):

    def __init__(self, weights_path='model/weights.pth', train_only_classifier=True, classes_number=2):
        super(MaskedFaceVgg, self).__init__()
        self.classes_number = classes_number
        vgg = models.vgg16()
        vgg.classifier[6] = nn.Linear(4096, self.classes_number, bias=True)
        self.features = vgg.features
        self.avgpool = vgg.avgpool
        self.classifier = vgg.classifier
        self.softmax = nn.Softmax(1)

        if weights_path:
            import os 
            print(os.getcwd())
            weights = torch.load(weights_path)
            try:
                self.load_state_dict(weights, strict=True)
            except RuntimeError:
                weights = MaskedFaceVgg.prefixed_weights_2_pytorch_vgg_weights(weights)
                self.load_state_dict(weights, strict=True)

        if train_only_classifier:
            self.__freeze_convolutional_layers()


    def __freeze_convolutional_layers(self):
        for layer in self.features:
            for param in layer.parameters():
                param.requires_grad = False


    def get_feature_vector(self, x):
        x = self.features(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        return x

    def classify(self, x):
        x = self.classifier(x)
        x = self.softmax(x)
        return x

    def forward(self, x):
        x = self.get_feature_vector(x)
        x = self.classify(x)
        return x

    @staticmethod
    def vgg_face_dag_2_pytorch_vgg_weights(vgg_dag_weights):
        for k1, k2 in zip(VGG_FACE_DAG_KEYS, PYTORCH_VGG_KEYS):
            vgg_dag_weights[k2] = vgg_dag_weights[k1]
            del vgg_dag_weights[k1]
        # delete last layer weights, since it's not compatible for our custom number of classes
        vgg_dag_weights.pop('classifier.6.weight')
        vgg_dag_weights.pop('classifier.6.bias')
        return vgg_dag_weights

    @staticmethod
    def prefixed_weights_2_pytorch_vgg_weights(pytorch_vgg_weights):
        '''
        Converts an ordered dict representing the model weights to make it compatible with the model.
        
        Each key is modified in the following way:

        '0.features.0.weight' --> 'features.0.weights'
        '''
        for k1, k2 in zip(PREFIXED_KEYS, PYTORCH_VGG_KEYS):
            pytorch_vgg_weights[k2] = pytorch_vgg_weights[k1]
            del pytorch_vgg_weights[k1]
        return pytorch_vgg_weights
