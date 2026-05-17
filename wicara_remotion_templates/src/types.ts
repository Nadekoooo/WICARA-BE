import {BaseTemplateSpec} from './helpers';
export type TemplateComponent = React.FC<{spec: BaseTemplateSpec}>;
export type TemplateRegistryEntry = {
  templateId: string;
  componentName: string;
  defaultSpec: BaseTemplateSpec;
};