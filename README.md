# Project Title

This project is a core component of our 8th grade data science curriculum, designed to provide students with an interactive platform to enhance their understanding of data analysis and visualization. It allows students to create and share their data visualizations, post screenshots, and provide constructive feedback to their peers—all within a virtual learning environment. By fostering a culture of collaboration and peer review, the project helps students develop essential skills in data literacy, critical thinking, and effective communication.

The current iteration of this project is called **DataDeck**, which is accessible at [www.datadeck.dev](http://www.datadeck.dev). DataDeck is an evolving platform that, in its future state, aims to become a comprehensive Flipgrid alternative, incorporating a range of features including voice, images, text, and video to facilitate richer interactions and discussions.

## Table of Contents

1. [About the Project](#about-the-project)
2. [Getting Started](#getting-started)
3. [Contributing](#contributing)
4. [Best Practices](#best-practices)
5. [License](#license)
6. [Contact](#contact)

## About the Project

This project is being developed and maintained by PREP-KC high school students, under the guidance of their in-house developer. It's part of an educational initiative aimed at providing real-world experience to students in software development and open-source collaboration. The primary goal is to create an accessible and effective platform that replaces the functionality of Flipgrid, while tailoring it specifically to the needs of our educational environment. By focusing on features like data visualization sharing, peer feedback, and various multimedia capabilities, we are building a tool that is both versatile and impactful for students and educators alike.

This project was developed in response to the discontinuation of Flipgrid, which had been a valuable tool for our 500+ students taking the 8th grade data science course. With Flipgrid going away, we saw the need to create an educational alternative—one built by educators and students, for educators and students. DataDeck is designed to meet the specific needs of our learning community, providing a familiar yet improved experience that supports meaningful engagement and communication.

### Key Features

- **Create a Class**: Educators can easily create classes to manage student participation.
- **Generate Student Accounts**: Generate student accounts based on fun, engaging characters, making it easier for students to get started.
- **Post Data Visualizations**: Students can post their data visualizations, including screenshots, for feedback from peers.
- **Peer Feedback and Voting**: Students can leave comments and vote based on different criteria, fostering a collaborative learning environment.
- **Interactive Layouts**: The platform features fun and interactive layouts, providing a fresh way for students to engage with data online.

## Getting Started

This project is a Django-based project built on Python 3.

### Prerequisites

Make sure Python 3 is installed and run the following commands to install Django and other required packages:

```bash
pip install django
pip install celery
pip install django-widget-tweaks
pip install jsonschema
pip install Pillow
pip install openpyxl
pip install reportlab
```

### First Time Run

To set up the database for the first time, run:

```bash
python manage.py migrate
```

### Setup Admin

To create a superuser for accessing the Django admin interface, run:

```bash
python manage.py createsuperuser
```

### Running the Server

To start the development server, run:

```bash
python manage.py runserver
```

### Deploy Command

To collect static files for deployment, run:

```bash
python manage.py collectstatic
```

### Old Commands (Not Currently Needed)

Celery Worker - No need to run currently:

```bash
celery -A engagekc worker --loglevel=info
celery -A engagekc beat --loglevel=info
```

## Contributing

We welcome contributions from anyone interested in supporting this project! Whether it's improving the documentation, fixing bugs, adding new features, or helping with other tasks, your efforts are greatly appreciated.

### How to Contribute

If you're new to open source contributions, don't worry. This project is a learning environment, especially for students who are gaining hands-on experience. We aim to make the contribution process simple and supportive.

## Best Practices

To keep things simple, we recommend that students pull directly from the main branch. This helps ensure everyone is working with the latest version of the project. However, for external contributors or more complex contributions, follow these steps:

1. Fork the project.
2. Create your feature branch (`git checkout -b feature/new-feature`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature/new-feature`).
5. Open a Pull Request.

### Code of Conduct

Please note that we have a [Code of Conduct](CODE_OF_CONDUCT.md) in place. All contributors are expected to adhere to it.

## License

This project is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License](LICENSE). Feel free to use and modify the project, but make sure to include the original attribution and abide by the non-commercial terms.

## Contact

For questions or suggestions, please reach out to us:
- **Project Team Lead**: PREP-KC In-House Developer
- **Student Contributors**: PREP-KC High School Students

For more information, visit [PREP-KC's website](https://prepkc.org).

---
We appreciate your interest and look forward to building a great project together!

[End with an encouraging statement about collaboration or the project's goals.]