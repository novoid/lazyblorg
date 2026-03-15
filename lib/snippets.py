# -*- coding: utf-8; mode: python; -*-

import config
import re
import logging
import copy


class SnippetException(Exception):
    """
    Exception for snippet resolution errors (loops, invalid references).
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class SnippetResolver(object):
    """
    Resolves snippet references in blog entries.

    Snippets are blog entries tagged with 'lbsnippet'. They can be
    referenced from other entries using [[id:snippet-id]] or bare
    id:snippet-id syntax. When resolved, the snippet content replaces
    the reference.
    """

    # Pattern for [[id:something]] links (Org-mode internal links)
    BRACKET_ID_LINK_RE = re.compile(r'\[\[id:([^\]]+)\]\]')
    # Pattern for [[id:something][description]] links (should warn)
    DESCRIBED_ID_LINK_RE = re.compile(r'\[\[id:([^\]]+)\]\[([^\]]+)\]\]')
    # Pattern for bare id:something references
    BARE_ID_RE = re.compile(r'(?<!\[)id:(\S+?)(?=[\s,;.!?\)\]\}]|$)')

    def __init__(self, blog_data):
        self.blog_data = blog_data
        self.snippet_dict = {}
        self._build_snippet_dict()

    def _build_snippet_dict(self):
        """Build lookup dict mapping snippet IDs to their entries."""
        for entry in self.blog_data:
            if entry.get('category') == config.SNIPPET:
                snippet_id = entry.get('id')
                if snippet_id:
                    self.snippet_dict[snippet_id] = entry
                    logging.debug("SnippetResolver: found snippet '%s'" % snippet_id)

        logging.debug("SnippetResolver: found %d snippets" % len(self.snippet_dict))

    def resolve_all(self):
        """
        Main entry point. Resolves all snippet references.

        First resolves snippet-within-snippet references, then resolves
        all non-snippet entries. Returns blog_data with snippet entries removed.

        @param return: blog_data with snippets resolved and snippet entries removed
        """

        if not self.snippet_dict:
            return self.blog_data

        # First pass: resolve snippets within snippets
        for snippet_id, snippet_entry in self.snippet_dict.items():
            self._resolve_entry_snippets(snippet_entry, [snippet_id])

        # Second pass: resolve snippets in all non-snippet entries
        for entry in self.blog_data:
            if entry.get('category') != config.SNIPPET:
                self._resolve_entry_snippets(entry, [])

        # Remove snippet entries from blog_data
        return [e for e in self.blog_data if e.get('category') != config.SNIPPET]

    def _resolve_entry_snippets(self, entry, expansion_chain):
        """
        Walk entry['content'] list, expanding snippet references.
        Also resolves rawcontent.

        @param entry: blog entry dict
        @param expansion_chain: list of snippet IDs in current expansion path (for loop detection)
        """

        if 'content' not in entry:
            return

        new_content = []
        for i, element in enumerate(entry['content']):
            expanded = self._expand_element(element, entry, new_content, expansion_chain)
            new_content.extend(expanded)
        entry['content'] = new_content

        # Also resolve rawcontent
        if 'rawcontent' in entry:
            entry['rawcontent'] = self._resolve_rawcontent(entry['rawcontent'], expansion_chain)

    def _expand_element(self, element, entry, content_before, expansion_chain):
        """
        For ['par', text] elements, check for snippet references.
        Decides inline vs block replacement.

        @param element: content element (list like ['par', text])
        @param entry: the containing blog entry
        @param content_before: list of content elements before this one
        @param expansion_chain: list of snippet IDs for loop detection
        @param return: list of elements to replace this element with
        """

        if not isinstance(element, list) or len(element) < 2 or element[0] != 'par':
            return [element]

        text = element[1]
        refs = self._find_snippet_references(text)

        if not refs:
            return [element]

        # Check for described links and warn
        described = self.DESCRIBED_ID_LINK_RE.findall(text)
        for ref_id, desc in described:
            if ref_id in self.snippet_dict:
                logging.warning(
                    "Snippet reference [[id:%s][%s]] has a description which will be ignored. "
                    "Use [[id:%s]] instead." % (ref_id, desc, ref_id))

        # Determine if block or inline replacement
        # Block: the entire paragraph is one snippet reference
        stripped = text.strip()
        is_block = False
        if len(refs) == 1:
            ref_id = refs[0]
            # Check if the paragraph is entirely this one reference
            bracket_form = '[[id:%s]]' % ref_id
            bare_form = 'id:%s' % ref_id
            if stripped == bracket_form or stripped == bare_form:
                is_block = True

        if is_block:
            ref_id = refs[0]
            return self._block_replace(ref_id, entry, content_before, expansion_chain)
        else:
            return [['par', self._inline_replace(text, refs, expansion_chain)]]

    def _find_snippet_references(self, text):
        """
        Find snippet references in text that reference known snippets.

        Finds [[id:snippet-id]] and bare id:snippet-id patterns.

        @param text: string to search
        @param return: list of snippet IDs found
        """

        refs = []

        # Find described links first (to exclude them from bracket matches)
        described_ids = set()
        for match in self.DESCRIBED_ID_LINK_RE.finditer(text):
            ref_id = match.group(1)
            if ref_id in self.snippet_dict:
                described_ids.add(ref_id)
                refs.append(ref_id)

        # Find bracket links [[id:...]]
        for match in self.BRACKET_ID_LINK_RE.finditer(text):
            ref_id = match.group(1)
            if ref_id in self.snippet_dict and ref_id not in described_ids:
                refs.append(ref_id)

        # Find bare id:... references
        for match in self.BARE_ID_RE.finditer(text):
            ref_id = match.group(1)
            if ref_id in self.snippet_dict:
                refs.append(ref_id)

        return refs

    def _block_replace(self, snippet_id, entry, content_before, expansion_chain):
        """
        Replace a paragraph-only snippet reference with all snippet content elements.
        Adapts heading levels to context.

        @param snippet_id: ID of the snippet to expand
        @param entry: the containing entry
        @param content_before: list of content elements before insertion point
        @param expansion_chain: list of IDs for loop detection
        @param return: list of content elements from the snippet
        """

        self._check_loop(snippet_id, expansion_chain)

        snippet = self.snippet_dict[snippet_id]
        snippet_content = copy.deepcopy(snippet.get('content', []))

        # Resolve nested snippets within this snippet's content
        if snippet_content:
            temp_entry = {'content': snippet_content}
            self._resolve_entry_snippets(temp_entry, expansion_chain + [snippet_id])
            snippet_content = temp_entry['content']

        # Adapt heading levels
        snippet_content = self._adapt_heading_levels(snippet_content, entry, content_before)

        return snippet_content

    def _inline_replace(self, text, ref_ids, expansion_chain):
        """
        Replace snippet references inline within text.
        Works for single-paragraph snippets; warns for multi-element snippets.

        @param text: the paragraph text
        @param ref_ids: list of snippet IDs to replace
        @param expansion_chain: list of IDs for loop detection
        @param return: modified text
        """

        for ref_id in ref_ids:
            self._check_loop(ref_id, expansion_chain)

            snippet = self.snippet_dict[ref_id]
            snippet_content = snippet.get('content', [])

            # Resolve nested snippets
            resolved_content = copy.deepcopy(snippet_content)
            if resolved_content:
                temp_entry = {'content': resolved_content}
                self._resolve_entry_snippets(temp_entry, expansion_chain + [ref_id])
                resolved_content = temp_entry['content']

            # Extract text from snippet content
            par_elements = [e for e in resolved_content if isinstance(e, list) and e[0] == 'par']
            if len(resolved_content) > len(par_elements):
                logging.warning(
                    "Snippet '%s' contains non-paragraph elements (headings, lists, etc.) "
                    "but is used inline. Only paragraph text will be substituted." % ref_id)

            snippet_text = ' '.join(e[1] for e in par_elements) if par_elements else ''

            # Replace described links first
            described_pattern = r'\[\[id:' + re.escape(ref_id) + r'\]\[[^\]]*\]\]'
            text = re.sub(described_pattern, snippet_text, text)

            # Replace bracket links
            bracket_pattern = r'\[\[id:' + re.escape(ref_id) + r'\]\]'
            text = re.sub(bracket_pattern, snippet_text, text)

            # Replace bare id: references
            bare_pattern = r'(?<!\[)id:' + re.escape(ref_id) + r'(?=[\s,;.!?\)\]\}]|$)'
            text = re.sub(bare_pattern, snippet_text, text)

        return text

    def _adapt_heading_levels(self, snippet_content, entry, content_before):
        """
        Adapt heading levels in snippet content to match the context.

        Find the previous heading in the article content before the
        insertion point and compute offset.

        @param snippet_content: list of content elements from snippet
        @param entry: the containing entry
        @param content_before: list of content elements before insertion point
        @param return: snippet_content with adapted heading levels
        """

        # Find first heading in snippet content
        first_snippet_heading_level = None
        for element in snippet_content:
            if isinstance(element, list) and element[0] == 'heading':
                first_snippet_heading_level = element[1]['level']
                break

        if first_snippet_heading_level is None:
            return snippet_content  # No headings to adapt

        # Find last heading level in content before insertion
        prev_heading_level = None
        for element in reversed(content_before):
            if isinstance(element, list) and element[0] == 'heading':
                prev_heading_level = element[1]['level']
                break

        if prev_heading_level is None:
            # Use entry's own level + 1 as the context level
            prev_heading_level = entry.get('level', 1)

        # Compute offset: make snippet headings one level below the previous heading
        offset = (prev_heading_level + 1) - first_snippet_heading_level

        if offset == 0:
            return snippet_content

        # Apply offset to all headings
        adapted = []
        for element in snippet_content:
            if isinstance(element, list) and element[0] == 'heading':
                new_element = copy.deepcopy(element)
                new_element[1]['level'] = element[1]['level'] + offset
                adapted.append(new_element)
            else:
                adapted.append(element)

        return adapted

    def _resolve_rawcontent(self, rawcontent, expansion_chain):
        """
        Replace snippet references in rawcontent strings with the snippet's rawcontent.
        Uses only the body portion (strips the entry heading line).

        @param rawcontent: raw Org-mode source string
        @param expansion_chain: list of IDs for loop detection
        @param return: modified rawcontent
        """

        # Replace [[id:snippet-id]] references
        for match in self.BRACKET_ID_LINK_RE.finditer(rawcontent):
            ref_id = match.group(1)
            if ref_id in self.snippet_dict:
                self._check_loop(ref_id, expansion_chain)
                snippet_raw = self._get_snippet_body_rawcontent(ref_id)
                rawcontent = rawcontent.replace('[[id:%s]]' % ref_id, snippet_raw)

        # Replace bare id:... references
        for match in self.BARE_ID_RE.finditer(rawcontent):
            ref_id = match.group(1)
            if ref_id in self.snippet_dict:
                self._check_loop(ref_id, expansion_chain)
                snippet_raw = self._get_snippet_body_rawcontent(ref_id)
                bare_pattern = r'(?<!\[)id:' + re.escape(ref_id) + r'(?=[\s,;.!?\)\]\}]|$)'
                rawcontent = re.sub(bare_pattern, snippet_raw, rawcontent)

        return rawcontent

    def _get_snippet_body_rawcontent(self, snippet_id):
        """
        Get the body portion of a snippet's rawcontent, stripping the
        heading line, CLOSED line, and LOGBOOK/PROPERTIES drawers.

        @param snippet_id: ID of the snippet
        @param return: body rawcontent string
        """

        snippet = self.snippet_dict[snippet_id]
        rawcontent = snippet.get('rawcontent', '')

        lines = rawcontent.split('\n')
        body_start = 0
        in_drawer = False

        for i, line in enumerate(lines):
            stripped = line.strip()
            if i == 0 and stripped.startswith('*'):
                # Skip heading line
                continue
            elif stripped.startswith('CLOSED:'):
                # Skip CLOSED status line
                continue
            elif stripped == ':LOGBOOK:' or stripped == ':PROPERTIES:':
                # Enter drawer, skip it
                in_drawer = True
                continue
            elif in_drawer:
                if stripped == ':END:':
                    in_drawer = False
                continue
            else:
                # First non-metadata line found
                body_start = i
                break

        return '\n'.join(lines[body_start:]).strip()

    def _check_loop(self, snippet_id, expansion_chain):
        """
        Check if expanding this snippet would create a loop.

        @param snippet_id: ID about to be expanded
        @param expansion_chain: list of IDs already in the expansion path
        @raises SnippetException: if loop detected
        """

        if snippet_id in expansion_chain:
            chain_str = ' → '.join(expansion_chain + [snippet_id])
            raise SnippetException(
                "Snippet loop detected: %s" % chain_str)
