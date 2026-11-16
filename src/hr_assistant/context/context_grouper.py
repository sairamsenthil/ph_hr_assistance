
import re


class ContextGrouper:

    BULLET_PATTERN = re.compile(
        r"^\s*(?:"
        r"[a-zA-Z]\s+"
        r"|[\uf0b7\u2022\u25aa\u25cf]\s*"
        r"|[-*]\s+"
        r")",
        re.IGNORECASE,
    )

    STAGE_HEADING_PATTERN = re.compile(
        r"^\s*\d+\.\s*Stage\s+\d+\s*$",
        re.IGNORECASE,
    )

    def is_bullet(self, paragraph):

        text = paragraph.strip()

        text = re.sub(
            r"^\d+\s*\n",
            "",
            text,
        ).strip()

        return bool(
            self.BULLET_PATTERN.match(text)
        )

    def is_heading(self, paragraph):

        text = paragraph.strip()

        if self.STAGE_HEADING_PATTERN.match(text):
            return True

        if re.match(
            r"^\d+\.\s+(Appeals|Records|Using mediation)$",
            text,
            re.IGNORECASE,
        ):
            return True

        return False

    def split_embedded_headings(self, paragraphs):

        processed = []

        pattern = re.compile(
            r"(?im)(?:^|\n)\s*(\d+\.\s*Stage\s+\d+)\s*$"
        )

        for paragraph in paragraphs:

            text = paragraph["text"].strip()
            index = paragraph["paragraph_index"]

            matches = list(pattern.finditer(text))

            if not matches:

                processed.append(paragraph)
                continue

            last_match = matches[-1]

            preceding_text = text[:last_match.start()].strip()
            heading_text = last_match.group(1).strip()

            if preceding_text:

                processed.append({
                    "paragraph_index": index,
                    "text": preceding_text,
                })

            processed.append({
                "paragraph_index": index,
                "text": heading_text,
            })

        return processed

    def group_paragraphs(self, paragraphs):

        paragraphs = self.split_embedded_headings(
            paragraphs
        )

        groups = []
        current_group = []

        for paragraph in paragraphs:

            index = paragraph["paragraph_index"]
            text = paragraph["text"].strip()

            if not text:
                continue

            item = {
                "paragraph_indexes": [index],
                "text": text,
            }

            if not current_group:

                current_group = [item]
                continue

            previous_text = current_group[-1]["text"]

            # A new heading starts a new group
            if self.is_heading(text):

                groups.append(
                    self.merge_group(current_group)
                )

                current_group = [item]

            # Attach bullets to the current group
            elif self.is_bullet(text):

                current_group.append(item)

            # Attach content to a list introduction
            elif previous_text.rstrip().endswith((":", ":-")):

                current_group.append(item)

            # Attach content to a standalone heading
            elif self.is_heading(previous_text):

                current_group.append(item)

            else:

                groups.append(
                    self.merge_group(current_group)
                )

                current_group = [item]

        if current_group:

            groups.append(
                self.merge_group(current_group)
            )

        return groups

    @staticmethod
    def merge_group(items):

        return {
            "paragraph_indexes": [
                index
                for item in items
                for index in item["paragraph_indexes"]
            ],
            "text": "\n\n".join(
                item["text"]
                for item in items
            ),
        }
