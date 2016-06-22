def add_file(repo, branch, message, filename, contents):
    """
    Add a new file to a new branch in a GitHub repo
    """

    # Get commit then git commit (not sure about the difference)
    commit = repo.get_branch('master').commit
    git_commit = repo.get_git_commit(commit.sha)

    # We need to include all the files in the master branch
    tree_input = []
    for element in repo.get_git_tree(commit.sha).tree:
        tree_input.append(InputGitTreeElement(element.path,
                                              element.mode,
                                              element.type,
                                              sha=element.sha))

    # We now make a blob with the new file contents and add it to the tree
    blob = repo.create_git_blob(content=contents, encoding="utf-8")
    tree_input.append(InputGitTreeElement(filename, "100644", "blob", sha=blob.sha))

    # We make a new tree, commit, and branch
    tree = repo.create_git_tree(tree=tree_input)
    commit = repo.create_git_commit(tree=tree, message=message, parents=[git_commit])
    ref = repo.create_git_ref(ref="refs/heads/{0}".format(branch), sha=commit.sha)
