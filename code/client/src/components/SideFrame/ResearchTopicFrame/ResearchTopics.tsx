export type ResearchTopic = {
  id: number;
  title: string;
  description: string;
  description_augmented: string;
};

export const researchTopicsPhysics: ResearchTopic[] = [
  {
    id: 1,
    title:
      "Modelling heavy quark bound states in ultrarelativistic heavy-ion collisions at the LHC at CERN",
    description:
      "This project focuses on heavy quarkonia (charmonium, bottomonium) in high-energy collisions at LHC, CERN. It aims to use quarkonia as a thermometer for studying high temperatures (over 10^12K) in heavy-ion collisions. The project involves simulating the thermalization of quark-antiquark pairs in a gluon environment, using quantum chromodynamics theory. This requires computer simulations instead of perturbation theory due to strong quark-gluon interactions. The project will also explore an open quantum systems approach, a technique from condensed matter physics, to understand how quarkonium reaches thermal equilibrium.",
    description_augmented:
      "This project focuses on heavy quarkonia (charmonium, bottomonium) in high-energy collisions at LHC, CERN. It aims to use quarkonia as a thermometer for studying high temperatures (over 10^12K) in heavy-ion collisions. The project involves simulating the thermalization of quark-antiquark pairs in a gluon environment, using quantum chromodynamics theory. This requires computer simulations instead of perturbation theory due to strong quark-gluon interactions. The project will also explore an open quantum systems approach, a technique from condensed matter physics, to understand how quarkonium reaches thermal equilibrium.",
  },
  {
    id: 2,
    title: "Nevanlinna spectral reconstruction",
    description:
      "This project focuses on simulating quantum systems with strong interactions, a key area in theoretical physics. It involves studying these systems across various energy scales, such as nuclear matter in high-temperature collisions and electron dynamics in materials. A major challenge is conducting these simulations in an artificial 'imaginary time domain,' which requires reconstructing relevant physics data for practical use. This reconstruction is an inverse problem, tackled using modern data analysis methods. The thesis explores solving these inverse problems through Bayesian inference and the Nevanlinna analytic continuation technique, a method related to the Pade approximation.",
    description_augmented:
      "This project focuses on simulating quantum systems with strong interactions, a key area in theoretical physics. It involves studying these systems across various energy scales, such as nuclear matter in high-temperature collisions and electron dynamics in materials. A major challenge is conducting these simulations in an artificial 'imaginary time domain,' which requires reconstructing relevant physics data for practical use. This reconstruction is an inverse problem, tackled using modern data analysis methods. The thesis explores solving these inverse problems through Bayesian inference and the Nevanlinna analytic continuation technique, a method related to the Pade approximation.",
  },
  {
    id: 3,
    title: "Quantum Brownian Motion",
    description:
      'This project explores quantum Brownian motion, a concept crucial in quantum computing and ultra cold quantum gases research. It investigates how to measure the temperature of atoms at extremely low temperatures using the quantum behavior of probe particles. This Bachelor thesis covers the "Theory of open quantum systems," providing a foundational understanding of quantum and classical Brownian motion. It includes developing software to simulate the one-dimensional Caldeira-Leggett model, enhancing skills in numerical simulation for complex quantum systems.',
    description_augmented:
      'This project explores quantum Brownian motion, a concept crucial in quantum computing and ultra cold quantum gases research. It investigates how to measure the temperature of atoms at extremely low temperatures using the quantum behavior of probe particles. This Bachelor thesis covers the "Theory of open quantum systems," providing a foundational understanding of quantum and classical Brownian motion. It includes developing software to simulate the one-dimensional Caldeira-Leggett model, enhancing skills in numerical simulation for complex quantum systems.',
  },
];

export const researchTopicsML: ResearchTopic[] = [
  {
    id: 1,
    title: "Predictive Analytics for E-commerce Sales Forecasting",
    description:
      "This project aims to develop a predictive model for forecasting e-commerce sales using historical sales data and other relevant features like product categories, seasonal trends, and promotional activities. The project will employ classical machine learning techniques, such as linear regression, decision trees, and random forests, to analyze patterns and predict future sales. This research could help e-commerce businesses in inventory management, marketing strategy planning, and optimizing sales operations.",
    description_augmented:
      "This project aims to develop a predictive model for forecasting e-commerce sales using historical sales data and other relevant features like product categories, seasonal trends, and promotional activities. The project will employ classical machine learning techniques, such as linear regression, decision trees, and random forests, to analyze patterns and predict future sales. This research could help e-commerce businesses in inventory management, marketing strategy planning, and optimizing sales operations.",
  },
  {
    id: 2,
    title: "Real-time Anomaly Detection in Network Traffic",
    description:
      "The goal of this project is to develop a real-time anomaly detection system for monitoring network traffic to identify potential security threats like intrusions or network failures. By applying unsupervised machine learning techniques, such as clustering and outlier detection algorithms, the system will analyze traffic patterns to flag unusual activities. This project is crucial for enhancing cybersecurity measures and maintaining network integrity.",
    description_augmented:
      "The goal of this project is to develop a real-time anomaly detection system for monitoring network traffic to identify potential security threats like intrusions or network failures. By applying unsupervised machine learning techniques, such as clustering and outlier detection algorithms, the system will analyze traffic patterns to flag unusual activities. This project is crucial for enhancing cybersecurity measures and maintaining network integrity.",
  },
  {
    id: 3,
    title: "Enhancing Deep Learning Efficiency with Pruned Neural Networks",
    description:
      "This project aims to investigate the impact of neural network pruning techniques on the computational efficiency and performance of deep learning models. By systematically reducing the complexity of networks while maintaining accuracy, the project seeks to develop lightweight models suitable for deployment in resource-constrained environments, such as mobile devices and embedded systems. The research will involve experimenting with various pruning methods, analyzing their effects on different deep learning architectures, and proposing an optimized pruning strategy that balances efficiency and performance.",
    description_augmented:
      "This project aims to investigate the impact of neural network pruning techniques on the computational efficiency and performance of deep learning models. By systematically reducing the complexity of networks while maintaining accuracy, the project seeks to develop lightweight models suitable for deployment in resource-constrained environments, such as mobile devices and embedded systems. The research will involve experimenting with various pruning methods, analyzing their effects on different deep learning architectures, and proposing an optimized pruning strategy that balances efficiency and performance.",
  },
];
