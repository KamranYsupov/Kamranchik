from repositories.resume import RepositoryResumes


class ResumesService:
    def __init__(self, repository_resumes: RepositoryResumes):
        self._repository_resumes = repository_resumes

    async def get_resume(self, **kwargs):
        return self._repository_resumes.get(**kwargs)

    async def get_list(self, **kwargs):
        return self._repository_resumes.list(**kwargs)
