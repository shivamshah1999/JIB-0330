## Greenhouse Accelerator Interactive Knowledge Hub<br>

# Release Notes
## v 1.0

### Features

_User Features_
 - Users navigate a branching path by answering questions about their business and interests to discover resources and media related to sustainable business practices.
 - Users can favorite any page for immediate access later.
 - Users can access previous stories from a 'History' page under 'Profile'.
 - Users may present a slideshow of their story from the 'History' page.
 - Users can update their profile as needed.

_Admin Features_
 - Admins can upload and maintain media for distribution to users.
 - Admins can create and edit story engines with a full suite of content creation tools under 'Editor'.
    - Admins can set the Live Engine, which defines which engine the users explore.
    - Admins can export and import engine data for archiving or direct editing.
    - Admins can use the built-in content creation tools to create engines, pages in engines, content for pages, and navigable structure in an engine.
 - Admins can manage user and admin accounts.

### Known Issues

- Database: If a user's account is _directly edited_ on Firebase, the application may not reflect the change to the user's information. Avoid directly editing user information in the database.
- Editor: Engines must be saved to the database with a name that matches the 'story_id' of the Engine. In some cases, it has been demonstrated that it is possible to circumnavigate this rule. However, the exact steps taken to get to this result could not be determined.
- Editor: Undetermined circumstances occasionally cause an open engine to produce multiple open tabs in the editor UI. Closing all engines causes duplicate tabs to go away. Be sure to save work before closing an engine to remedy this bug.



# Interactive Knowledge Hub Installation Guide 

## Prerequisites

The Knowledge Hub is a web application which is live as of 4/23/2021. No special prerequisites are required for user or administrative operations aside from connection to the Internet and a modern browser such as Chrome or Firefox. No special installation is required before use. 

Note that the KHub has not been designed or tested for mobile devices. UI Elements may appear out of place or inconveniently sized. We recommend using the KHub from a personal computer.

## Dependencies

Site Administrators are required to maintain accounts with <a href="https://firebase.google.com/">Firebase</a>, <a href="https://cloud.google.com/run">Google Cloud Run</a>, <a href="https://github.com/">GitHub</a>, <a href="https://sendgrid.com/">SendGrid</a>, and <a href="https://www.tiny.cloud/">TinyMCE</a> for long term maintenance. 

No special dependencies are required to access the KHub as a user or content author. Content for the KHub can be created and edited only with a KHub admin account.

The KHUB is hosted with Google Firebase. Database routing is handled by Flask using Google Cloud Run. UI and interactivity are laregly written in JS and JQuery. Necessary code libraries are hosted with the code, excepting the <a href="https://www.tiny.cloud/">TinyMCE rich text editor</a> used in the content authoring portion of the application.

*NOTE on Future Development:*<br>
Though not required, we recommend use of the <a href="https://firebase.google.com/docs/emulator-suite">Firebase Emulator Suite</a>  for further application development. Using the suite, a developer may download and run a fully local version of the KHub--including a local database--creating a sandbox environment where new features can be developed and tested without disturbing the state of the live application.

## Access

There is no need to download or install an application to use the KHub. Users and content authors can access the KHub at https://gaknowledgehub.web.app.

The code repository for the KHub is [FILL IN HERE].

## Build Instructions

While the code base has been provided to Greenhouse Accelerator, the KHub is live as of 4/23/2021. The code provided must be hosted and served by the services noted above. However, this step has been taken by the development team and no further builds or compilation are required to use the app.

*For Future Development:*<br>
<a href="https://cloud.google.com/sdk/docs/install">Google Cloud Run</a> and <a href="https://firebase.google.com/docs/cli">Firebase Tools</a> installations are required on the developer's machine for server deployment. These steps need to be executed once for a developer.
1. To install Cloud Run, follow the <a href="https://cloud.google.com/sdk/docs/install">link</a> instructions. 
2. To install Firebase Tools, use the command ```npm install firebase-tools``` from the project root directory in the terminal.
3. Run ```gcloud init``` from the command line or terminal and follow instructions.
4. Run ```node_modules\.bin\firebase login``` from the commmand line or terminal to log in to Firebase.

For each deployment, run ```deploy prod``` from the project root directory.


## Run Instructions

Users and administrators can access the KHub at https://gaknowledgehub.web.app. 

## Troubleshooting
There are no known issues accessing the KHub as a user or administrator. Users and admins must create an account for access. Note that Users and Admins have differing feature sets. Only Users are prompted to 'Begin Story' and create a history. Only an administrator has access to the content creation tools. Only an administrator may grant adminstrator rights to another user. Any given real person is free to create multiple accounts i.e. one admin account and one user account.

See known issues in release notes for issues _using_ the appliction.