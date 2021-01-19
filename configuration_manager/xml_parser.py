import xml.etree.ElementTree as ET
import errno
import os


class Parser(object):
    """
    This class provides functions for parsing an xml file
    and converting it into Python dictionary type for manipulation.
    """

    @classmethod
    def load_xml(cls, file):
        """Parses an XML section into an element tree.

        Parameters
        ----------
        file : object
            XML file containg XML data

        Returns
        -------
        xmltree: ElementTree instance
            The parsed XML
        """
        try:
            cls.__xmltree = ET.parse(file)
        except FileNotFoundError as e:
            raise e  # TODO: a better exception handling
        else:
            return cls.__xmltree

    @classmethod
    def __build_child_nodes(cls, child_list):
        """Helper function to build nested items.

        Parameters
        ----------
        child_list :
            The parent element of the nested elements.

        Returns
        -------
        child_nodes: List
            Nested items of an element
        """
        child_nodes = list()
        for element in child_list:
            if element:
                # treat like dict
                if len(element) == 1 or element[0].tag != element[1].tag:
                    child_nodes.append(cls.xml2dict(element))
                # treat like list
                elif element[0].tag == element[1].tag:
                    child_nodes.append(cls.build_child_nodes(element))
            elif element.text:
                text = element.text.strip()
                if text:
                    child_nodes.append(text)
        return child_nodes

    @classmethod
    def convert_xml2dict(cls, parent_element):
        """Converts an xml.etree.ElementTree into a Python Dictionary data type.

        Parameters
        ----------
        parent_element : xml.etree.ElementTree.Element
            The root element

        Returns
        -------
        nodes: dictionary
            Dictionary created from xml.etree.ElementTree
        """
        nodes = dict()
        if parent_element.items():
            # Case: if root element has attributes
            nodes.update(dict(parent_element.items()))
        for element in parent_element:
            if element:
                # Case: child elements
                if len(element) == 1 or element[0].tag != element[1].tag:
                    # If the first two tags in a series are different,
                    # then the series is different. Keep on building
                    # dictionary.
                    running_dictionary = cls.convert_xml2dict(element)
                else:
                    # Build a list of nested elements sharing the same tag name
                    running_dictionary = cls.__build_child_nodes(element)
                # if the tag has attributes, add those to the dict
                if element.items():
                    running_dictionary = {element[0].tag:
                                            cls.__build_child_nodes(element)}
                    running_dictionary.update(dict(element.items()))
                nodes.update({element.tag: running_dictionary})
            elif element.items():
                # Case: if the element has attributes then add them
                # into dictionary
                nodes.update({element.tag: dict(element.items())})
            # Finally: No child tags and no attributes
            else:
                nodes.update({element.tag: element.text})
        return nodes
