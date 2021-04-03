# GCWIR
**Good Citizens Wear It Right!**

Several studies suggest a proper use of the mask can be helpful to fight the Sars-CoV-2 outbreak, especially when applied in closed environment.
This is a demo project which aims to show how we can exploit AI to detect people that don't use masks, or they wear it wrongly.

We've uses the Vgg-16 architecture as our model, pretrained for facial recognition.
We've freezed the convolutive layers and concentrated our work on training the multilayer perceptron for classifying faces:
* label *correct* if the person in the image wears the mask correctly
* label *incorrect* if the person doesn't wear the mask at all or wears it in a wrong way

The dataset used for the MLP training can be found [here](https://github.com/cabani/MaskedFace-Net)

The *Bridge* class uses the webcam of the machine has being running on to take an image, classifies it through the model, and communicate to Arduino in order to blink a green or red LED, according to the outcome of the classification.

We've added the capability to our model to improve over time, by sending (upon user interaction with an Arduino platform) a labeled feature vector to a listening server. The server stores theese data on a simple sqlite database. Then, this server is periodically queried for new feature vector by a client, containig an exact copy of the model we use for classification.
Here, we provide these new samples to our MLP, performing a gradient descent update (though a complete retraining would definitely be better), save the new weights of our model and send them back to the server. This will forward them to the bridge class, which will load them into his model (hopefully improving it).

The projects is built on *python 3.8.5*


# Usage
After installing the required packages, you can just run the *start.py* script to get an idea of how the project works. Or you can run the different modules (Bridge, Server and Client) separately.
You will need an *Arduino-compatible platform* corectly set up and plugged into the machine which runs the Brdige module to enjoy the demo.
If you wish to use our *Dataset* class out of the box, you will need to put the CMFD and IMFD folders (you'll find them through the dataset link we've provided) in the root folder of the project.


# Future works
This is only a demo project, feel free to extend it in any fashion you like.


# Credits
* Parkhi, Omkar M., Andrea Vedaldi, and Andrew Zisserman. "Deep Face Recognition." BMVC. Vol. 1. No. 3. 2015, [link](https://arxiv.org/abs/1409.1556)
* Yang Liu, Samuel Albanie, Arsha Nagrani and Andrew Zisserman, "Use What You Have: Video Retrieval Using Representations From Collaborative Experts", BMVC 2019 [link](https://www.robots.ox.ac.uk/~albanie/pytorch-models.html)
* Adnane Cabani, Karim Hammoudi, Halim Benhabiles, and Mahmoud Melkemi, "MaskedFace-Net - A dataset of correctly/incorrectly masked face images in the context of COVID-19", Smart Health, ISSN 2352-6483, Elsevier, 2020, [link](https://www.sciencedirect.com/science/article/pii/S2352648320300362?via%3Dihub)
* Karim Hammoudi, Adnane Cabani, Halim Benhabiles, and Mahmoud Melkemi,"Validating the correct wearing of protection mask by taking a selfie: design of a mobile application "CheckYourMask" to limit the spread of COVID-19", CMES-Computer Modeling in Engineering & Sciences, Vol.124, No.3, pp. 1049-1059, 2020, [link](https://www.techscience.com/CMES/v124n3/39927)
