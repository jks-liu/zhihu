# 使用TypeScript发布NPM包（2021年版）

本文受篇幅限制，很多东西无法讲得特别细致，详细信息可以查看文中链接。

# 步骤1：在GitHub上创建一个新的项目
- 添加READMD
- 添加.gitignore，类型选择node
- 添加一个合适的开源license
- Clone仓库到本地

# 步骤2：添加TypeScript和ESLint支持
本小节的很多步骤参考自[Getting Started - Linting your TypeScript Codebase](https://github.com/typescript-eslint/typescript-eslint/blob/master/docs/getting-started/linting/README.md)。

[注意TSLint已经过时，不推荐使用，请使用ESLint](https://github.com/palantir/tslint/issues/4534)。

- `npm i -D typescript`
    * `-D`表示开发环境的依赖。由于最终发布到npm的包只包含JavaScript，所以使用这个包的用户不需要TypeScript。
    * 同时也不建议将TypeScript全局安装，否则其他的开发者可能使用一个不同版本的TypeScript，这可能会导致问题。
- `npm i -D eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin`
    * 显然和Lint相关的东西都只在开发环境中使用。
- 在根目录添加一个名为`.eslintrc.js`的文件，其内容如下：
    ```js
    module.exports = {
        root: true,
        parser: '@typescript-eslint/parser',
        plugins: [
            '@typescript-eslint',
        ],
        extends: [
            'eslint:recommended',
            'plugin:@typescript-eslint/recommended',
            "plugin:node/recommended",
            "prettier",
        ],
    };
    ```
    * 默认ESLint会解析JavaScript代码，但是不解析TypeScript代码。所以我们通过`parser: '@typescript-eslint/parser'`来指定使用TypeScript的解析器。
    * `plugins: ['@typescript-eslint']`表示使用TypeScript的插件（即上面安装的`@typescript-eslint/eslint-plugin`）。
    * `extends: [ ... ]`声明使用的扩展
        - `eslint:recommended`表示使用ESLint的建议规则
        - `plugin:@typescript-eslint/recommended`表示使用TypeScript的建议规则
        - 另外两个下面再讲
- [`npm i -D eslint-plugin-node`](https://github.com/mysticatea/eslint-plugin-node)
    * 给ESLint添加Node.js相关的规则
    * `.eslintrc.js`中的`"plugin:node/recommended"`表示使用这里推荐的规则
- 在根目录添加一个名为`.eslintignore`的文件，此文件告诉ESLint不用lint这些文件夹里的文件。其内容如下：
    ```py
    # don't ever lint node_modules
    node_modules
    # don't lint build output (make sure it's set to your correct build folder name)
    lib
    ```
    * `node_modules`是依赖包的文件夹，所以不需要lint。
    * `lib`是存放构建文件的输出文件夹，所以不需要lint。注：`lib`这个名字只是我个人的选择，你也可以选择其它文件夹作为输出文件夹。常见的名字包括：`dist`, `build`, `out`, `release`等等。
- `node ./node_modules/typescript/bin/tsc --init`：初始化TypeScript配置文件`tsconfig.json`，修改以下配置：
    * `"declaration": true`：让tsc自动生成对用的`.d.ts`文件。
    * `"outDir": "./lib"`：指定输出文件夹，和上面说的`lib`一致。
    * `"include": ["src"]`：按照我的个人习惯，源代码文件（除了测试文件）都放在`src`文件夹里。注意：`include`配置和`compilerOptions`配置是同一个级别的，不像上面两个是从属关系。
- 在`package.json`中的`scripts`配置中添加`"build": "tsc"`，以后就可以通过执行`npm run build`来使用TypeScript编译工程到`lib`文件夹。

# 步骤3：使用`jest`作为测试框架
- `npm i -D jest @types/jest ts-jest`
    * 与测试相关的包显然也只在开发环境中使用。
    * 同样，我们通过[`ts-jest`](https://github.com/kulshekhar/ts-jest)包来让Jest支持TypeScript代码。
- `npx ts-jest config:init`：初始化Jest配置文件`jest.config.js`，并修改，我的配置如下：
    ```js
    /** @type {import('ts-jest/dist/types').InitialOptionsTsJest} */
    module.exports = {
        preset: 'ts-jest',
        testEnvironment: 'node',

        "transform": {
            "^.+\\.(ts|tsx)$": "ts-jest"
        },
    };
    ```
    * `preset: 'ts-jest'`：使用`ts-jest`的预设配置
    * `testEnvironment: 'node'`：使用Node.js作为测试环境
    * `"transform": {}`：告诉Jest哪些代码需要使用`ts-jest`来转换
    * 其它配置请参考[Jest配置文件](https://jestjs.io/docs/en/configuration)。
- 在`package.json`中的`scripts`配置中添加`"test": "jest"`，以后就可以通过命令`npm t`来执行测试。
- 编写测试文件
    * Jest默认会执行`__tests__`文件夹下的TypeScript文件，所以我们将测试代码放在`__tests__`文件夹下。
    * 由于上面我们在`tsconfig.json`中配置了`"include": ["src"]`，所以测试文件不会被编译，最终的npm包中也不会有测试文件。

# 步骤4：使用`prettier`来格式化代码
- `npm i -D prettier`
- `echo {}> .prettierrc.json`告诉编辑器等工具你要使用的格式化工具是`prettier`。
- 新建一个`.prettierignore`文件，内容如下（请根据自己的情况自行增删）：
    ```py
    # Ignore artifacts:
    node_modules
    lib
    coverage
    ```
- `npm i -D eslint-config-prettier`：安装`eslint-config-prettier`，这个包是用来让`eslint`支持`prettier`的。 并修改`.eslintrc.js`：回顾前文，我们在`extends`中添加的`"prettier"`。
    * 注意，`"prettier"`一定要放在`extends`的最后一个
    * 由于ESLint的规则和Prettier的规则略有细微差别，所以我们需要`eslint-config-prettier`提供的规则来extends ESLint的规则。

如果你使用VS Code，下面的步骤可以使其支持`prettier`的格式化：
- 安装[`Prettier - Code formatter`](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode)扩展
- 打开VS Code的设置（`Ctrl-Shift-P` -> `references: Open Workspace Settings (JSON)`），将以下配置添加到其中：
    ```json
    {
        "editor.defaultFormatter": null,
        "[javascript]": {
            "editor.defaultFormatter": "esbenp.prettier-vscode"
        },
        "[typescript]": {
            "editor.defaultFormatter": "esbenp.prettier-vscode"
        },
        "[jsonc]": {
            "editor.defaultFormatter": "esbenp.prettier-vscode"
        },
        "editor.formatOnType": true,
        "editor.formatOnSave": true,
    }
    ```
    * `"esbenp.prettier-vscode"`：即上面扩展提供的Prettier格式化器
    * 上面配置了`JavaScript`，`TypeScript`和`JSON`在修改和保存时都会自动格式化。参考[官方文档](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode)修改上面配置来满足你自己的需求。

# 步骤5：实现你的库的功能
用你的库实现任何你想要的功能

# 步骤6：发布到npm
- 注册[npm](https://www.npmjs.com/signup)账号
- `npm adduser`：添加npm账号到本机
- `npm run build`：打包你的库
- `npm publish`：发布到npm

# 步骤7：最后别忘了给本文点赞。
- 请追更本文，因为前端发展很快，所以我在必要时会更新文章。
- 本文是我写[Markdown-It Plugin for Zhihu CommonMark](https://github.com/jks-liu/markdown-it-zhihu-common)时的记录，上面有什么我讲得不明白的，可以参考。


