# SlideSpeak coding challenge: Build a PowerPoint to PDF marketing tool

## The challenge!

Build a front-end implementation as well as a back-end service to convert PowerPoint documents to PDF format. This
should be done by implementing a simple **Next.js** front-end that posts a file to a **Python** server. You don’t have
to do the converting logic yourself as you can use unoconv or unoserver to do this (you can see more about this in the
acceptance criteria). The front-end is also already implemented in the /frontend folder. You only need to add the
necessary logic to switch between the steps and convert the file via the API that you're going to build.

- Design: [https://www.figma.com/file/CRfT0MVMqIV8rAK6HgSnKA/SlideSpeak-Coding-Challenge?type=design&t=6m2fFDaRs72CowZH-6](https://www.figma.com/file/CRfT0MVMqIV8rAK6HgSnKA/SlideSpeak-Coding-Challenge?type=design&t=6m2fFDaRs72CowZH-6)

## Acceptance criteria

### Back-end API

- Should be implemented in Python.
- Converting PowerPoints to PDF can be done with `unoconv` or `unoserver` via Docker if you want to be fancy 😀. You
  don’t need to implement the converting logic yourself.
  - [How to use unoserver via docker](https://gist.github.com/kgoedecke/44955d0b0b1ed4112bcfd3e237e135c0), this will
    create an API that you can use based on [this](https://github.com/libreofficedocker/unoserver-rest-api)
    documentation.
    - Using unoserver is nice-to-have (but the preferred way), if you find unoconv easier use it instead
- Under the the hood the API:

  1. Convert the attached file to PDF
  2. Upload the PowerPoint and PDF file to Amazon S3
     via [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
  3. Create a presigned URL for the user to download

     [https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html)

     [https://medium.com/@aidan.hallett/securing-aws-s3-uploads-using-presigned-urls-aa821c13ae8d](https://medium.com/@aidan.hallett/securing-aws-s3-uploads-using-presigned-urls-aa821c13ae8d)

  4. Return the presigned S3 url to the client which allows the user to download the file (by opening the url in new
     tab)

- Queuing to process multiple requests at a time

### Front-end app

- The front-end should in terms of UX work similarly
  to [https://app.slidespeak.co/powerpoint-optimizer](https://app.slidespeak.co/powerpoint-optimizer)

## General Requirements:

- Use conventional commit message style: https://www.conventionalcommits.org/en/v1.0.0/
- Lint your code
- Keep commits clean

## Nice to haves / tips

- Uses unoserver to convert PowerPoint to PDF via docker compose
- The logic of the front-end ideally should not rely on useEffect too much since it can be difficult to track what is
  happening
- Tests
- API documentation
