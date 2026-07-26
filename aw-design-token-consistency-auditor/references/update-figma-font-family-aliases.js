const collections = await figma.variables.getLocalVariableCollectionsAsync();
const typographyCollection = collections.find((collection) => collection.name === "Typography DT");
const otherCollection = collections.find((collection) =>
  collection.name === "Other" || collection.name === "Other Collection"
);

if (!typographyCollection) throw new Error("Missing Figma variable collection: Typography DT");
if (!otherCollection) throw new Error("Missing Figma variable collection: Other / Other Collection");

const variables = await figma.variables.getLocalVariablesAsync();
const typographyFontFamily =
  "Geist, Geist Variable, Inter, Noto Sans SC, PingFang SC, Microsoft YaHei, sans-serif";
const rootFontFamilyVariable = variables.find(
  (variable) =>
    variable.variableCollectionId === typographyCollection.id &&
    variable.name === "typography/font-family"
);
const fontFamilyVariable = variables.find(
  (variable) =>
    variable.variableCollectionId === otherCollection.id &&
    variable.name === "Font Family"
);

if (!fontFamilyVariable) throw new Error("Missing Other Collection variable: Font Family");
if (!rootFontFamilyVariable) throw new Error("Missing Typography DT variable: typography/font-family");

const targets = variables.filter(
  (variable) =>
    variable.variableCollectionId === typographyCollection.id &&
    variable.name !== "typography/font-family" &&
    variable.name.endsWith("/font-family")
);

const description =
  "Figma runtime note: this style-level token aliases to Other/Font Family because Figma may not recognize comma-separated font family stacks from Typography DT string variables. The root typography/font-family token stays as the DESIGN.md/CSS-aligned font stack for audit coverage.";
const rootDescription =
  "Audit alignment token: keep this value as the DESIGN.md/CSS comma-separated font stack. For actual Figma text binding, route style-level typography/*/font-family variables to Other/Font Family.";

const rootModeIds = Object.keys(rootFontFamilyVariable.valuesByMode || {});
for (const modeId of rootModeIds) {
  rootFontFamilyVariable.setValueForMode(modeId, typographyFontFamily);
}
rootFontFamilyVariable.description = rootDescription;

const updated = [];
for (const variable of targets) {
  const modeIds = Object.keys(variable.valuesByMode || {});
  for (const modeId of modeIds) {
    variable.setValueForMode(modeId, {
      type: "VARIABLE_ALIAS",
      id: fontFamilyVariable.id,
    });
  }
  variable.description = description;
  updated.push(variable.name);
}

return {
  typographyCollection: typographyCollection.name,
  otherCollection: otherCollection.name,
  rootFontFamily: rootFontFamilyVariable.name,
  rootValue: typographyFontFamily,
  aliasTarget: fontFamilyVariable.name,
  rootUpdated: true,
  updatedCount: updated.length,
  updated,
};
