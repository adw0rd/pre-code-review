pre-code-review
===============

It's a hooks for preliminary check a python code to ``pep8`` and ``pyflakes``, as well as check commit message to format ``<issue title> [<prefix>-<id>] <comment>``.


Installation:
--------------

Install Dependences::

    sudo apt-get install pyflakes pep8

Install Hooks::

    cd ~/work
    git clone git://github.com/adw0rd/pre-code-review.git pre-code-review
    
    ln -s /home/<username>/work/pre-code-review/pre-commit.py /home/<username>/work/<project>/.git/hooks/pre-commit
    ln -s /home/<username>/work/pre-code-review/commit-msg.py /home/<username>/work/<project>/.git/hooks/commit-msg
    
    chmod +x ~/work/<project>/.git/hooks/pre-commit
    chmod +x ~/work/<project>/.git/hooks/commit-msg
