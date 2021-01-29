# Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more
#  contributor license agreements; and to You under the Apache License,
#  Version 2.0."

from xml.etree import ElementTree


class Parser:
    @classmethod
    def load_xml(cls, file):
        """Parses an XML section into an element tree.

        Parameters
        ----------
        file : object
            XML file containing the XML data

        Returns
        -------
        ElementTree instance
        """
        try:
            # self.__xmltree = ElementTree.parse(file)
            cls.__xmltree = ElementTree.parse(file)
        except FileNotFoundError as e:
            raise e  # TODO: a better exception handling
        else:
            return cls.__xmltree

    # @classmethod
    def __build_nested_nodes(self, parent_element):
        """
        Helper function to build the list of nested elements.

        Parameters
        ----------
        parent_element : xml.etree.ElementTree.Element
            The parent element of the nested elements.

        Returns
        -------
        nested_nodes: list
            List of nested elements
        """
        nested_nodes = list()
        for element in parent_element:
            if element:
                # Case: nested elements
                if len(element) == 1 or element[0].tag != element[1].tag:
                    # Case: If the depth is one or the first two tags
                    # in the hierarchy are different, then the series
                    # is different.
                    nested_nodes.append(self.convert_xml2dict(element))
                elif element[0].tag == element[1].tag:
                    # Case: nested elements share the same tag name.
                    nested_nodes.append(self.__build_nested_nodes(element))
            elif element.text:
                # Case: At the deepest level of the hierarchy
                text = element.text.strip()  # remove all leading and trailing whitespaces
                if text:
                    nested_nodes.append(text)
        return nested_nodes

    def convert_xml2dict(self, parent_element):
        """Converts an xml.etree.ElementTree into a Python Dictionary data type.

        Parameters
        ----------
        parent_element : xml.etree.ElementTree.Element
            The root element

        Returns
        -------
        xml_dictionary : dictionary
            Dictionary built out of the elements of xml.etree.ElementTree
        """
        xml_dictionary = dict()
        if parent_element.items():
            # Case: if the parent element has attributes,
            # then add them into the dictionary
            xml_dictionary.update(dict(parent_element.items()))
        else:
            for child_element in parent_element:
                if child_element:
                    # Case: nested elements
                    if (len(child_element) == 1 or
                            child_element[0].tag != child_element[1].tag):
                        # Case: If the depth is one or the first two tags
                        # in the hierarchy are different, then the series
                        # is different. Keep on building dictionary.
                        xml_dictionary.update({child_element.tag:
                                               self.convert_xml2dict(child_element)})
                    else:
                        # Case: nested elements share the same tag name.
                        # add them as a list with the shared tag as the
                        # dictionary key. A list is required for configuring
                        # the logger handlers by logging.config API.
                        xml_dictionary.update({child_element.tag:
                                              self.__build_nested_nodes(child_element)})
                elif child_element.items():
                    # Case: if the element has attributes
                    # then add them into dictionary
                    xml_dictionary.update({child_element.tag:
                                          dict(child_element.items())})
                # Case: No child tags and no attributes
                else:
                    xml_dictionary.update({child_element.tag: child_element.text})
        return xml_dictionary
