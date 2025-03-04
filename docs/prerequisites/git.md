# GitHub Account

You will need a [GitHub](https://github.com) account to contribute to this repository via pull requests or to access a JupyterHub environment such as [NASA Openscape's 2i2c](https://openscapes.2i2c.cloud).

This [document](https://docs.github.com/en/get-started/start-your-journey/creating-an-account-on-github#signing-up-for-a-new-personal-account) will guide you through the steps of signing up for a free personal GitHub account.

## Git
Once you have a GitHub account, it is important to understand fundamental `Git` concepts. Familiarize yourself with `Git` by referring to this [introductory guide](https://docs.github.com/en/get-started/getting-started-with-git) and [this handy cheatsheet](https://training.github.com/downloads/github-git-cheat-sheet.pdf).

[This installation guide](https://github.com/git-guides/install-git) provides instructions on how to install `Git` in your system (Windows, Linux, or Mac) if it is not already installed. 

## GitHub Authentication
There are several ways to authenticate your GitHub account. We will use a [SSH authentication method](https://docs.github.com/en/authentication/connecting-to-github-with-ssh).

1. Generate a new SSH key: Open your terminal (or Git Bash on Windows) and run the following command: 
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```
2. Copy the SSH key:  Copy the contents of your SSH key file, located at `~/.ssh/id_ed25519.pub`, to your clipboard. 
3. Add the SSH Key to GitHub: Navigate to https://github.com/settings/keys on your GitHub and click the "New SSH Key" button. Provide a title for your key and paste the contents you copied in Step 2 into the key field. Click "Add SSH Key" to save.

You are now set up to use SSH for connecting to GitHub.

## Git Clone

To get started, clone this [GEDI data tutorials](https://github.com/ornldaac/gedi_tutorials) git repository by running the following command on your terminal (or Git bash in Windows):

```bash
git clone git@github.com:ornldaac/gedi_tutorials.git
```
