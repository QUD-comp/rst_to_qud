import argparse

import test

"""Module to call evaluate_transform from command line."""

parser = argparse.ArgumentParser(description="Evaluate transform_rst on a corpus")
parser.add_argument('rst_path', help="Path of the folder of the RST trees.")
parser.add_argument('gold_qud_path', help="Path of the folder containing the human-annotated QUD trees.")
parser.add_argument('transformed_path', help="Path to write the transformed trees to.")
parser.add_argument('result_filename', help="Path of the file to write the evaluation results to.")

args = parser.parse_args()


test.evaluate_transform(args.rst_path,
                   args.gold_qud_path,
                   args.transformed_path,
                   args.result_filename)
