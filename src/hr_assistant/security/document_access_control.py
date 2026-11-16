
class DocumentAccessControl:

    ROLE_PERMISSIONS = {
        "employee": {"public"},
        "manager": {"public", "manager"},
        "hr": {"public", "manager", "hr"},
        "admin": {"public", "manager", "hr", "admin"},
    }

    VALID_ACCESS_LEVELS = {
        "public",
        "manager",
        "hr",
        "admin",
    }

    def can_access(self, user_role, document_access_level):

        # Unknown roles are denied
        if user_role not in self.ROLE_PERMISSIONS:
            return False

        # Missing or invalid access metadata is denied
        if document_access_level not in self.VALID_ACCESS_LEVELS:
            return False

        allowed_levels = self.ROLE_PERMISSIONS[user_role]

        return document_access_level in allowed_levels

    def filter_documents(self, documents, user_role):

        if not isinstance(documents, list):
            raise ValueError("documents must be a list")

        if user_role not in self.ROLE_PERMISSIONS:
            return []

        authorized_documents = []

        for document in documents:

            if not isinstance(document, dict):
                continue

            access_level = document.get("access_level")

            if self.can_access(
                user_role=user_role,
                document_access_level=access_level,
            ):
                authorized_documents.append(document)

        return authorized_documents
