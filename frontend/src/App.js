import React, { useEffect, useState } from 'react';
import { Table } from 'antd';
import qs from 'qs';
import { Col, Row,Divider,Image,Input,Typography,Layout, Flex } from 'antd';


const { Title } = Typography;
const { Search } = Input;
const { Header, Footer, Sider, Content } = Layout;

const headerStyle = {
  backgroundColor: '#fff',
  textAlign: 'center',
  minHeight: 200,

};
const contentStyle = {
};

const footerStyle = {
};

const layoutStyle = {
  borderRadius: 8,
  overflow: 'hidden',
  width: 'calc(100% - 8px)',
  maxWidth: 'calc(100% - 8px)',
};

const columns = [
  {
    title: 'Image',
    dataIndex: 'default_thumbnail_url',
    render: (record) => <Image width={record.width} height={record.height} src={record.url} />,
    width: '10%',
  },
  {
    title: 'Video ID',
    dataIndex: 'videoId',
    width: '5%',
  },
  {
    title: 'Channel ID',
    dataIndex: 'channelId',
    width: '5%',
  },
  {
    title: 'Title',
    dataIndex: 'title',
    width: '10%',
    sorter: (a, b) => a.title.length - b.title.length,
    sortDirections: ['descend']
  },
  {
    title: 'Description',
    dataIndex: 'description',
    width: '50%',
    filters: [
      {
        text: 'RCB',
        value: 'RCB',
      },
      {
        text: 'CSK',
        value: 'CSK',
      }
      ],
    onFilter: (value: string, record) => record.description.search(value) != -1,
    filterSearch: true,
  },
  {
    title: 'Published At',
    dataIndex: 'publishedAt',
    width: '5%',
  }
  ];
const getRandomuserParams = (params) => ({
  results: params.pagination?.pageSize,
  page: params.pagination?.current,
  ...params,
});
const App = () => {
  const [data, setData] = useState();
  const [loading, setLoading] = useState(false);
  const [tableParams, setTableParams] = useState({
    pagination: {
      current: 1,
      pageSize: 10,
    },
  });
  const fetchData = () => {
    setLoading(true);
    fetch(`http://0.0.0.0:8080/list?page=${tableParams.pagination.current}&page_limit=${tableParams.pagination.pageSize}`)
      .then((res) => res.json())
      .then(({ page, showing,videos }) => {
        console.log(videos[0]);
        setData(videos);
        setLoading(false);
        setTableParams({
          ...tableParams,
          pagination: {
            ...tableParams.pagination,
            total: 200,
            // 200 is mock data, you should read it from server
            // total: data.totalCount,
          },
        });
      }).catch((error) => {
  console.log(error)
});
  };
  useEffect(() => {
    fetchData();
  }, [JSON.stringify(tableParams)]);
  const handleTableChange = (pagination, filters, sorter) => {
    setTableParams({
      pagination,
      filters,
      ...sorter,
    });

    // `dataSource` is useless since `pageSize` changed
    if (pagination.pageSize !== tableParams.pagination?.pageSize) {
      setData([]);
    }
  };
  return (

    <Flex gap="middle" wrap="wrap">
    <Layout style={layoutStyle}>
      <Header style={headerStyle}>
                 <Title> Welcome to NewsFeed Project</Title>
                 <Title level={2}> My Name is Saurav Solanki. I did this project.</Title>
      </Header>

      <Content style={contentStyle}>

          <Row>

      <Col span={20} offset={2}>
                                   <Divider plain></Divider>

          <Search placeholder="input search loading default" loading />

                                   <Divider plain></Divider>


               <Title level={3}> Here is the list of videos: </Title>
            <Table
      columns={columns}
      rowKey={(record) => record.videoId}
      dataSource={data}
      pagination={tableParams.pagination}
      loading={loading}
      onChange={handleTableChange}
    />
      </Col>
    </Row>
      </Content>
    </Layout>

    </Flex>
  );
};
export default App;