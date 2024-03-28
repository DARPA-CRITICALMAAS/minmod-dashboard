var dagcomponentfuncs = (window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {});

dagcomponentfuncs.urlLink = function (props) {

    if (props.value && props.value.startsWith('http')) {
        return React.createElement(
            'a',
            { href: props.value, target: "_blank" },
            props.value
        );
    } else {
        return props.value
    }
};
